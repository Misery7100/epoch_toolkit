import logging
from enum import Enum
from typing import Any, List

from pydantic import BaseModel

# ----------------------- #


class LogLevel(Enum):
    debug = logging.DEBUG
    info = logging.INFO
    warning = logging.WARNING
    error = logging.ERROR
    critical = logging.CRITICAL

    @classmethod
    def get(cls, v):
        return getattr(cls, v, logging.INFO)


# ----------------------- #


class LogManager:
    loggers = {}

    @staticmethod
    def get_logger(name: str, log_level: LogLevel = LogLevel.info) -> logging.Logger:
        if name in LogManager.loggers:
            return LogManager.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(log_level.value)

        ch = logging.StreamHandler()
        ch.setLevel(log_level.value)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s :: %(name)s :: %(message)s"
        )

        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False
        LogManager.loggers[name] = logger

        return logger


# ----------------------- #


class LogMixin:
    __logger: logging.Logger

    # ....................... #

    def __init__(
        self,
        *args,
        logger_name: str = "default",
        log_level: str | LogLevel = LogLevel.info,
        **kwargs
    ) -> None:

        if isinstance(log_level, str):
            log_level = LogLevel.get(log_level)

        self.__logger = LogManager.get_logger(logger_name, log_level)

    # ....................... #

    def __preprocess_args__(self, args: List[Any]) -> List[Any]:
        def process_item(item: Any) -> Any:
            if isinstance(item, Enum):
                return item.value

            elif isinstance(item, list):
                return [process_item(sub_item) for sub_item in item]

            elif isinstance(item, dict):
                return {
                    process_item(key): process_item(value)
                    for key, value in item.items()
                }

            elif isinstance(item, BaseModel):
                return item.model_dump()

            else:
                return item

        return [process_item(arg) for arg in args]

    # ....................... #

    def info(self, msg: str, *args, **kwargs):
        args = self.__preprocess_args__(args)
        self.__logger.info(msg, *args, **kwargs)

    # ....................... #

    def error(self, msg: str, *args, **kwargs):
        args = self.__preprocess_args__(args)
        self.__logger.error(msg, *args, **kwargs)

    # ....................... #

    def warning(self, msg: str, *args, **kwargs):
        args = self.__preprocess_args__(args)
        self.__logger.warning(msg, *args, **kwargs)

    # ....................... #

    def debug(self, msg: str, *args, **kwargs):
        args = self.__preprocess_args__(args)
        self.__logger.debug(msg, *args, **kwargs)

    # ....................... #

    def critical(self, msg: str, *args, **kwargs):
        args = self.__preprocess_args__(args)
        self.__logger.critical(msg, *args, **kwargs)
