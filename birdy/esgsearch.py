import sys

import logging
logger = logging.getLogger(__name__)

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
        return parser

def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.WARN)
    logger.setLevel(logging.INFO)
    
    esgsearch = ESGSearch()
    parser = esgsearch.create_parser()            
    args = parser.parse_args()

if __name__ == '__main__':
    sys.exit(main())
