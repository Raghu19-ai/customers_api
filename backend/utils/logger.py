import logging
from logging.handlers import RotatingFileHandler
from utils.context import correlation_id_var


#  Correlation ID Filter
class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id_var.get() or "N/A"
        return True


logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)


#  Avoid duplicate handlers
if not logger.handlers:

    # File handler with rotation
    handler = RotatingFileHandler(
        "app.log",
        maxBytes=5 * 1024 * 1024,#5MB
        backupCount=3
    )

    # UPDATED FORMATTER (important)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(correlation_id)s | %(message)s"
    )

    handler.setFormatter(formatter)

    #  Attach filter
    handler.addFilter(CorrelationIdFilter())

    logger.addHandler(handler)


    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(formatter)

    #  Attach filter here also
    console.addFilter(CorrelationIdFilter())

    logger.addHandler(console)