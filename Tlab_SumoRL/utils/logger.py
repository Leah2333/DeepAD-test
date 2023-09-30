import logging
from Tlab_SumoRL.utils.config import CFG

loglevel_dict = {
    'debug':    logging.DEBUG,
    'info':     logging.INFO,
    'warning':  logging.WARNING,
    'error':    logging.ERROR,
    'critical': logging.CRITICAL
}

log_lvl = loglevel_dict[CFG.misc.loglevel.lower()]
log_fmt = "%(asctime)s [%(filename)s: %(lineno)d] " \
          "<%(levelname)s>: %(message)s"

logging.basicConfig(
    level=log_lvl,
    format=log_fmt
)

logger = logging.getLogger('log')
