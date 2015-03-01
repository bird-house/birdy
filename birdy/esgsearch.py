import sys

import logging
logger = logging.getLogger(__name__)

# see completer examples:
# https://github.com/kislyuk/argcomplete/blob/master/argcomplete/completers.py

# see argcomplete usage:
# https://gist.github.com/bewest/1202975
# https://github.com/conda/conda/blob/master/conda/cli/main.py

# activate argcomplete
# eval "$(register-python-argcomplete bin/esgsearch)"

def esgf_search_projects(prefix, parsed_args, **kwargs):
    choices = ("CMIP5", "CORDEX")
    return (choice for choice in choices if choice.startswith(prefix))
    
def esgf_search_experiments(prefix, parsed_args, **kwargs):
    choices = ("historical", "rcp26", "rcp85")
    return (choice for choice in choices if choice.startswith(prefix))

def esgf_search_variables(prefix, parsed_args, **kwargs):
    choices = ("ta", "tas", "pr")
    return (choice for choice in choices if choice.startswith(prefix))

class ESGSearch(object):
    """
    Command line client for esgf search.

    $ esgsearch -h
    """
    def __init__(self):
        pass

    def create_parser(self):
        """
        Generates parser to query esgf search on the command line.
        """
        import argparse

        parser = argparse.ArgumentParser(
            prog="esgsearch",
            #usage='''esgsearch [<options>] <command> [<args>]''',
            description="Query ESGF search",
            add_help=False,
            )
      
        parser.add_argument("--project", required=True).completer = esgf_search_projects
        parser.add_argument("--experiment", required=True).completer = esgf_search_experiments
        parser.add_argument("--variable", nargs="*").completer = esgf_search_variables

        subparsers = parser.add_subparsers(dest='command', title='commands')
        subparser = subparsers.add_parser("files", prog="esgsearch {0}".format("command"))

       

        # first sniff for basic debuggery, help fill in defaults
        ## try:
        ##     known, args = parser.parse_known_args()
        ## except:
        ##     parser.print_help( ) 

        real_parser = argparse.ArgumentParser(add_help=False)

        real_parser.add_argument("--project", required=True).completer = esgf_search_projects
        real_parser.add_argument("--experiment", required=True).completer = esgf_search_experiments
        real_parser.add_argument("--variable", nargs="*").completer = esgf_search_variables

        subparsers = real_parser.add_subparsers(dest='command', title='commands')
        subparser = subparsers.add_parser("files", prog="esgsearch {0}".format("command"))
        subparser.add_argument("--test")

        return parser, real_parser

def main():
    import argcomplete
    
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)
    logger.setLevel(logging.INFO)
    
    esgsearch = ESGSearch()
    parser,real_parser = esgsearch.create_parser()
    argcomplete.autocomplete(parser)
    args = real_parser.parse_args()

if __name__ == '__main__':
    sys.exit(main())
