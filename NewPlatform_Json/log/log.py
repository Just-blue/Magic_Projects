import logging
import logging.handlers
import datetime

DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

standard_handler = logging.StreamHandler()
standard_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                                                "%m-%d %H:%M:%S"))
standard_handler.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('all.log',encoding='utf-8')
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(processName)s - %(threadName)s - "
                                            "%(funcName)s -%(module)s[%(lineno)d] - %(message)s",
                                            "%m-%d %H:%M:%S"))
file_handler.setLevel(logging.DEBUG)

logger.addHandler(standard_handler)
logger.addHandler(file_handler)
