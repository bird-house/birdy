"""
Generic wps client
"""

import logging
from owslib.wps import WebProcessingService

SERVICE = "http://localhost:8093/wps"


def execute(wps, args):
    inputs = []
    # TODO: this is probably not the way to do it
    for key in args.__dict__.keys():
        if not key in ['identifier', 'output']:
            inputs.append( (key, str( getattr(args, key) )) )
    # list of tuple (output identifier, asReference attribute)
    outputs = [(args.output, True)]
    execution = wps.execute(args.identifier, inputs, outputs)
    monitor(execution, download=False)

def monitor(execution, sleepSecs=3, download=False, filepath=None):
    '''
    Convenience method to monitor the status of a WPS execution till it completes (succesfully or not),
    and write the output to file after a succesfull job completion.
    
    execution: WPSExecution instance
    sleepSecs: number of seconds to sleep in between check status invocations
    download: True to download the output when the process terminates, False otherwise
    filepath: optional path to output file (if downloaded=True), otherwise filepath will be inferred from response document
    
    '''
    
    while execution.isComplete()==False:
        execution.checkStatus(sleepSecs=sleepSecs)
        print 'Execution status: %s' % execution.status
        
    if execution.isSucceded():
        if download:
            execution.getOutput(filepath=filepath)
        else:
            for output in execution.processOutputs:               
                if output.reference is not None:
                    print 'Output URL=%s' % output.reference
    else:
        for ex in execution.errors:
            print 'Error: code=%s, locator=%s, text=%s' % (ex.code, ex.locator, ex.text)

def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.ERROR)
    
    wps = WebProcessingService(SERVICE, verbose=False, skip_caps=False)
    
    import argparse

    parser = argparse.ArgumentParser(
        description="%s: %s" % (wps.identification.title, wps.identification.abstract))
    subparsers = parser.add_subparsers(
        dest='identifier',
        title='subcommands',
        description='valid subcommands',
        help='additional help')
    for i in range(0, len(wps.processes)):
        process = wps.describeprocess(wps.processes[i].identifier)
        parser_process = subparsers.add_parser(process.identifier, help=process.abstract)

        for input in process.dataInputs:
            parser_process.add_argument('--'+input.identifier,
                                        dest=input.identifier,
                                       #default=False,
                                        action="store",
                                        help="%s" % (input.title)
                                )

        output_choices = [output.identifier for output in process.processOutputs]
        help_msg = "Output: "
        for output in process.processOutputs:
            help_msg = help_msg + '%s=%s, ' % (output.identifier, output.title)
        parser_process.add_argument(
            '--output',
            dest="output",
            default="output",
            choices=output_choices,
            action="store",
            help=help_msg
        )

    args = parser.parse_args()
    execute(wps, args)

