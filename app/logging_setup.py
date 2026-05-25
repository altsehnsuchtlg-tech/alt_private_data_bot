import logging


def configure_logging() -> None:
    """配置全局日志格式和级别。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
