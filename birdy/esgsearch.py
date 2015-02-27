import sys

import logging
logger = logging.getLogger(__name__)

# see completer examples:
# https://github.com/kislyuk/argcomplete/blob/master/argcomplete/completers.py

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
            )
        parser.add_argument("--debug",
                            help="enable debug mode",
                            action="store_true")
        parser.add_argument("--project", required=True).completer = esgf_search_projects
        parser.add_argument("--experiment", required=True).completer = esgf_search_experiments
        parser.add_argument("--variable", nargs="*").completer = esgf_search_variables

        subparsers = parser.add_subparsers(dest='command', title='commands')
        subparser = subparsers.add_parser("files", prog="esgsearch {0}".format("command"))
        subparser.add_argument("--test")

        return parser

def main():
    import argcomplete
    
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)
    logger.setLevel(logging.INFO)
    
    esgsearch = ESGSearch()
    parser = esgsearch.create_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

if __name__ == '__main__':
    sys.exit(main())
