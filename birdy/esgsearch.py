import sys

import logging
logger = logging.getLogger(__name__)

def esgf_search_projects(prefix, parsed_args, **kwargs):
    choices = ("CMIP5", "CORDEX")
    return (choice for choice in choices if choice.startswith(prefix))
    
def esgf_search_experiments(prefix, parsed_args, **kwargs):
    choices = ("historical", "rcp26", "rcp85")
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
        parser.add_argument("--project").completer = esgf_search_projects
        parser.add_argument("--experiment").completer = esgf_search_experiments
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
