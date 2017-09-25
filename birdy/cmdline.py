import sys
import os
from ._compat import urlparse
from owslib.wps import WebProcessingService, ComplexDataInput
from . import wpsparser
from .utils import fix_local_url, encode

import logging
logging.basicConfig(format='%(message)s', level=logging.WARN)
LOGGER = logging.getLogger("BIRDY")


def _wps(url, skip_caps=True, verify=False, token=None):
    wps = WebProcessingService(url, verbose=False, skip_caps=True)
    if hasattr(wps, 'verify'):
        wps.verify = verify
    if hasattr(wps, 'headers'):
        if token:
            # use access token to execute process
            wps.headers = {'Access-Token': token}
    try:
        if not skip_caps:
            wps.getcapabilities()
    except Exception:
        raise Exception('Could not access wps %s', url)
    return wps


class Birdy(object):
    """
    Birdy is a command line client for Web Processing Services.

    Documentation is available on readthedocs:
    http://birdy.readthedocs.org/en/latest/

    see help:
    $ birdy -h
    """
    outputs = {}
    complex_inputs = {}

    def __init__(self, service):
        self.service = service
        self.wps = _wps(service, skip_caps=False)

    def create_parser(self):
        """
        Generates parser to execute WPS processes on the command line.

        See Python argparse documentation:
        https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
        https://docs.python.org/2/howto/argparse.html
        https://docs.python.org/2/library/argparse.html#module-argparse
        https://argparse.googlecode.com/svn/trunk/doc/parse_args.html

        lazy parsing subparser:
        http://stackoverflow.com/questions/22742450/argparse-on-demand-imports-for-types-choices-etc
        """
        import argparse
        from birdy import __version__

        parser = argparse.ArgumentParser(
            prog="birdy",
            usage='''birdy [<options>] <command> [<args>]''',
            description=wpsparser.parse_wps_description(self.wps),
        )
        parser.add_argument("--debug",
                            help="enable debug mode",
                            action="store_true")
        parser.add_argument('--version', action='version',
                            version='%(prog)s {}'.format(__version__))
        # parser.add_argument("--insecure", "-k",
        #                     help="Allow connections to SSL sites without certs.",
        #                     action="store_true")
        parser.add_argument(
            "--sync", '-s',
            help="Execute process in sync mode. Default: async mode.",
            action="store_true")
        parser.add_argument("--token", "-t",
                            help="Token to access the WPS service.",
                            action="store")
        subparsers = parser.add_subparsers(
            dest='identifier',
            title='command',
            description='List of available commands (wps processes)',
            help='Run "birdy <command> -h" to get additional help.'
        )

        for process in self.wps.processes:
            subparser = subparsers.add_parser(
                process.identifier,
                prog="birdy {0}".format(process.identifier),
                help=wpsparser.parse_process_help(process)
            )
            # subparser.set_defaults(func=self.execute)
            # lazy build of sub-command
            # TODO: maybe a better way to do this?
            # command = sys.argv[1]
            # if command==process.identifier:
            # TODO: this matching is too dangerous !!!
            if process.identifier in sys.argv:
                self.build_command(subparser, process.identifier)

        return parser

    def build_command(self, subparser, identifier):
        LOGGER.debug("build subparser for command=%s", identifier)

        process = self.wps.describeprocess(identifier)

        for input in process.dataInputs:
            subparser.add_argument(
                '--' + input.identifier,
                dest=input.identifier,
                required=wpsparser.parse_required(input),
                nargs=wpsparser.parse_nargs(input),
                # type=parse_type(input),
                choices=wpsparser.parse_choices(input),
                default=wpsparser.parse_default(input),
                action="store",
                help=wpsparser.parse_description(input),
            )
            if wpsparser.is_complex_data(input):
                mimetypes = ([str(value.mimeType) for value in input.supportedValues])
                self.complex_inputs[input.identifier] = mimetypes
        output_choices = [output.identifier for output in process.processOutputs]
        help_msg = "Output: "
        for output in process.processOutputs:
            help_msg = help_msg + str(output.identifier) + "=" + wpsparser.parse_description(output)\
                + " (default: all outputs)"
            self.outputs[output.identifier] = wpsparser.is_complex_data(output)
        subparser.add_argument(
            '--output',
            dest="output",
            nargs='*',
            choices=output_choices,
            action="store",
            help=help_msg
        )

    def execute(self, args):
        if args.debug:
            LOGGER.setLevel(logging.DEBUG)
            LOGGER.debug('using web processing service %s', self.service)

        if hasattr(args, 'token') and args.token:
            # use access token to execute process
            self.wps = _wps(self.service, skip_caps=False, token=args.token)

        inputs = []
        # inputs
        # TODO: this is probably not the way to do it
        for key in args.__dict__.keys():
            if key not in ['identifier', 'output', 'debug', 'sync', 'token']:
                values = getattr(args, key)
                # checks if single value (or list of values)
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    in_value = self._input_value(key, value)
                    if in_value is not None:
                        inputs.append((str(key), in_value))
        # outputs
        output = self.outputs.keys()
        if args.output is not None:
            output = args.output
        # checks if single value (or list of values)
        if not isinstance(output, list):
            output = [output]
        # list of tuple (output identifier, asReference attribute)
        outputs = [(str(identifier), self.outputs.get(str(identifier), True)) for identifier in output]
        # now excecute it ...
        # LOGGER.debug(outputs)
        if hasattr(args, 'sync') and args.sync is True:
            # TODO: sync is non-default and avail only in patched owslib
            execution = self.wps.execute(
                identifier=args.identifier,
                inputs=inputs, output=outputs,
                async=False)
        else:
            execution = self.wps.execute(args.identifier, inputs, outputs)

        # waits for result (async call)
        self.monitor(execution, download=False)
        return execution

    def _input_value(self, key, value):
        content = ''
        if key in self.complex_inputs:
            content = self._complex_value(key, value)
        else:
            content = self._literal_value(key, value)
        return content

    def _complex_value(self, key, value):
        LOGGER.debug("complex: key=%s, value=%s", key, value)
        url = fix_local_url(value)
        u = urlparse(self.wps.url)
        if 'localhost' in u.netloc:
            LOGGER.debug('use url: %s', url)
            content = ComplexDataInput(url)
        else:
            LOGGER.debug('encode content: %s', url)
            encoded = encode(url, self.complex_inputs[key])
            content = ComplexDataInput(encoded)
        return content

    def _literal_value(self, key, value):
        return value

    def monitor(self, execution, sleepSecs=3, download=False, filepath=None):
        """
        Convenience method to monitor the status of a WPS execution till it completes (succesfully or not),
        and write the output to file after a succesfull job completion.

        execution: WPSExecution instance
        sleepSecs: number of seconds to sleep in between check status invocations
        download: True to download the output when the process terminates, False otherwise
        filepath: optional path to output file (if downloaded=True), otherwise filepath
        will be inferred from response document
        """
        while execution.isComplete() is False:
            execution.checkStatus(sleepSecs=sleepSecs)
            LOGGER.info('[%s %d/100] %s', execution.status, execution.percentCompleted, execution.statusMessage)

        if execution.isSucceded():
            if download:
                execution.getOutput(filepath=filepath)
            else:
                LOGGER.info("Output:")
                for output in execution.processOutputs:
                    if output.reference is not None:
                        LOGGER.info('%s=%s (%s)' % (output.identifier, output.reference, output.mimeType))
                    else:
                        LOGGER.info('%s=%s' % (output.identifier, ", ".join(output.data)))
        else:
            for ex in execution.errors:
                LOGGER.warn('Error: code=%s, locator=%s, text=%s' % (ex.code, ex.locator, ex.text))


def main():
    import argcomplete

    LOGGER.setLevel(logging.INFO)

    service = os.environ.get("WPS_SERVICE", "http://localhost:8094/wps")

    mybirdy = Birdy(service)
    parser = mybirdy.create_parser()
    argcomplete.autocomplete(parser)

    args = parser.parse_args()
    mybirdy.execute(args)


if __name__ == '__main__':
    sys.exit(main())
