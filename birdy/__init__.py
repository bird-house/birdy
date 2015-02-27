import sys
from wpsparser import *

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)
logger = logging.getLogger(__name__)

class Birdy(object):
    """
    Birdy is a command line client for Web Processing Services.

    Documentation is available on readthedocs:
    http://birdy.readthedocs.org/en/latest/

    see help:
    $ birdy -h
    """
    OUTPUT_TYPE_MAP = {}
    
    def __init__(self, service):
        from owslib.wps import WebProcessingService
        try:
            self.wps = WebProcessingService(service, verbose=False, skip_caps=False)
        except:
            logger.exception('Could not access wps %s', service)
            raise

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

        parser = argparse.ArgumentParser(
            prog="birdy",
            usage='''birdy [<options>] <command> [<args>]''',
            description=parse_wps_description(self.wps),
            )
        parser.add_argument("--debug",
                            help="enable debug mode",
                            action="store_true")
        subparsers = parser.add_subparsers(
            dest='identifier',
            title='command',
            description='List of available commands (wps processes)',
            help='Run "birdy <command> -h" to get additional help.'
            )

        for process in self.wps.processes:
            subparsers.add_parser(process.identifier)
            subparser = subparsers.add_parser(
                process.identifier,
                prog="birdy {0}".format(process.identifier) ,
                help=parse_process_help(process)
                )
            #subparser.set_defaults(func=self.execute)
            # lazy build of sub-command
            # TODO: maybe a better way to do this?
            #command = sys.argv[1]
            #if command==process.identifier:
            # TODO: this matching is too dangerous !!!
            if process.identifier in sys.argv:
                self.build_command(subparser, process.identifier)

        return parser

    def build_command(self, subparser, identifier):
        logger.debug("build subparser for command=%s", identifier)
        
        process = self.wps.describeprocess(identifier)

        for input in process.dataInputs:
            subparser.add_argument(
                '--'+input.identifier,
                dest=input.identifier,
                required=parse_required(input),
                nargs=parse_nargs(input),
                #type=parse_type(input),
                choices=parse_choices(input),
                default=parse_default(input),
                action="store",
                help=parse_description(input),
            )
        output_choices = [output.identifier for output in process.processOutputs]
        help_msg = "Output: "
        for output in process.processOutputs:
           help_msg = help_msg + str(output.identifier) + "=" + parse_description(output) + " (default: all outputs)"
           self.OUTPUT_TYPE_MAP[output.identifier] = is_complex_data(output)
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
            logger.setLevel(logging.DEBUG)
            logger.debug('using web processing service %s', self.wps.url)
        
        inputs = []
        # inputs 
        # TODO: this is probably not the way to do it
        for key in args.__dict__.keys():
            if not key in ['identifier', 'output']:
                values = getattr(args, key)
                # checks if single value (or list of values)
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    inputs.append( (str(key), str(value) ) )
        # outputs
        output = self.OUTPUT_TYPE_MAP.keys()
        #logger.debug(output)
        if args.output is not None:
            output = args.output
        # checks if single value (or list of values)
        if not isinstance(output, list):
            output = [output]
        # list of tuple (output identifier, asReference attribute)
        outputs = [(str(identifier), self.OUTPUT_TYPE_MAP.get(identifier, True)) for identifier in output]
        # now excecute it ...
        #logger.debug(outputs)
        execution = self.wps.execute(args.identifier, inputs, outputs)
        # waits for result (async call)
        self.monitor(execution, download=False)

    def monitor(self, execution, sleepSecs=3, download=False, filepath=None):
        """
        Convenience method to monitor the status of a WPS execution till it completes (succesfully or not),
        and write the output to file after a succesfull job completion.

        execution: WPSExecution instance
        sleepSecs: number of seconds to sleep in between check status invocations
        download: True to download the output when the process terminates, False otherwise
        filepath: optional path to output file (if downloaded=True), otherwise filepath will be inferred from response document

        """

        while execution.isComplete()==False:
            execution.checkStatus(sleepSecs=sleepSecs)
            logger.info('Execution status: %s', execution.status)

        if execution.isSucceded():
            if download:
                execution.getOutput(filepath=filepath)
            else:
                logger.info("Output:")
                for output in execution.processOutputs:               
                    if output.reference is not None:
                        logger.info('%s=%s (%s)' % (output.identifier, output.reference, output.mimeType))
                    else:
                        logger.info('%s=%s' % (output.identifier, ", ".join(output.data)))
        else:
            for ex in execution.errors:
                logger.warn('Error: code=%s, locator=%s, text=%s' % (ex.code, ex.locator, ex.text))


def main():
    logger.setLevel(logging.INFO)
    
    from os import environ 
    service = environ.get("WPS_SERVICE", "http://localhost:8094/wps")
   
    mybirdy = Birdy(service)
    parser = mybirdy.create_parser()
            
    args = parser.parse_args()
    mybirdy.execute(args)

    ## try:
    ##     mybirdy.execute(args)
    ## except:
    ##     logger.exception('birdy execute failed!')
    ##     sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())


