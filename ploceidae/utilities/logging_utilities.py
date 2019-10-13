import logging
from os import makedirs, path

def configure_logging(log_level):
    artifacts = "artifacts"
    if not path.exists(artifacts):
        makedirs(artifacts)
    logging.basicConfig(level=log_level,
                        format='%(asctime)s : %(levelname)-5s : [	%(module)s - %(funcName)s] => %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=path.join(artifacts, "ploceidae.log"),
                        filemode='w')
    logging.getLogger('').addFilter(Filter())

class Filter(logging.Filter):

    def filter(self, record):
        print(record.pathname)
        return record.pathname.startswith("ploceidae.")