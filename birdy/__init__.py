"""
WPS command line client

see help:
$ birdy -h
"""

from wpsparser import *

import logging
logger = logging.getLogger(__name__)

class Birdy(object):
    OUTPUT_TYPE_MAP = {}
    
    def __init__(self):
        pass

    def execute(self, wps, args):
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
        #logging.debug(output)
        if args.output is not None:
            output = args.output
        # checks if single value (or list of values)
        if not isinstance(output, list):
            output = [output]
        # list of tuple (output identifier, asReference attribute)
        outputs = [(str(identifier), self.OUTPUT_TYPE_MAP.get(identifier, True)) for identifier in output]
        # now excecute it ...
        #logging.debug(outputs)
        execution = wps.execute(args.identifier, inputs, outputs)
        # waits for result (async call)
        monitor(execution, download=False)

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
            print 'Execution status: %s' % execution.status

        if execution.isSucceded():
            if download:
                execution.getOutput(filepath=filepath)
            else:
                print "Output:"
                for output in execution.processOutputs:               
                    if output.reference is not None:
                        print '%s=%s (%s)' % (output.identifier, output.reference, output.mimeType)
                    else:
                        print '%s=%s' % (output.identifier, ", ".join(output.data))
        else:
            for ex in execution.errors:
                print 'Error: code=%s, locator=%s, text=%s' % (ex.code, ex.locator, ex.text)

    def create_process_parser(self, subparsers, wps, identifier):
        process = wps.describeprocess(identifier)

        parser_process = subparsers.add_parser(
            process.identifier,
            prog="birdy {0}".format(process.identifier) ,
            help=parse_process_help(process)
            )

        for input in process.dataInputs:
            parser_process.add_argument(
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
        parser_process.add_argument(
            '--output',
            dest="output",
            nargs='*',
            choices=output_choices,
            action="store",
            help=help_msg
        )
    
    def create_parser(self, wps):
        """
        Generates commands to execute WPS processes on the command line.

        See Python argparse documentation:
        https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
        https://docs.python.org/2/howto/argparse.html
        https://docs.python.org/2/library/argparse.html#module-argparse
        https://argparse.googlecode.com/svn/trunk/doc/parse_args.html
        """

        import argparse
        import argcomplete
        import sys

        parser = argparse.ArgumentParser(
            #prog="birdy",
            usage='''birdy [-h] <command> [<args>]''',
            description=parse_wps_description(wps),
            )
        subparsers = parser.add_subparsers(
            dest='identifier',
            title='command',
            description='List of available commands (wps processes)',
            help='Run "birdy <command> -h" to get additional help.'
            )

        for process in wps.processes:
            parser_process = subparsers.add_parser(process.identifier)

        # autocomplete
        argcomplete.autocomplete(parser)

        # parse only birdy with command
        logging.debug(sys.argv)
        # TODO: check args
        #args = parser.parse_args(sys.argv[1:2])
        # check if called with command
        #if hasattr(args, "identifier"):
        #    create_process_parser(subparsers, wps, args.identifier)

        return parser

def main():
    from sys import exit
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)

    from os import environ 
    service = environ.get("WPS_SERVICE", "http://localhost:8094/wps")
    logging.debug('using wps %s', service)

    from owslib.wps import WebProcessingService
    try:
        wps = WebProcessingService(service, verbose=False, skip_caps=False)
    except:
        logging.exception('Could not access wps %s', service)
        exit(1)

    mybirdy = Birdy()
    parser = mybirdy.create_parser(wps)
    args = parser.parse_args()
    execute(wps, args)

