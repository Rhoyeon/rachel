import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s trace_id=%(trace_id)s %(message)s',
    )
