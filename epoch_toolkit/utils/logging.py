import logging
from enum import Enum
from typing import Any, List, Union

from pydantic import BaseModel

# ----------------------- #


class LogLevel(Enum):
    """Enumeration representing different log levels."""

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
    """A class that manages loggers for different modules."""

    loggers = {}

    @staticmethod
    def get_logger(name: str, log_level: LogLevel = LogLevel.info) -> logging.Logger:
        """
        Retrieves or creates a logger for the specified module name.

        Args:
            name (str): The name of the module.
            log_level (LogLevel, optional): The log level for the logger. Defaults to LogLevel.info.

        Returns:
            logging.Logger: The logger object.

        """

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
    """A mixin class that provides logging functionality."""

    __logger: logging.Logger

    # ....................... #

    def __init__(
        self,
        *args,
        logger_name: str = "default",
        log_level: Union[str, LogLevel] = LogLevel.info,
        **kwargs
    ) -> None:

        if isinstance(log_level, str):
            log_level = LogLevel.get(log_level)

        self.__logger = LogManager.get_logger(logger_name, log_level)

    # ....................... #

    def __preprocess_args__(self, args: List[Any]) -> List[Any]:
        """
        Preprocess the arguments by applying specific transformations to each item in the list.

        Args:
            args (List[Any]): The list of arguments to be preprocessed.

        Returns:
            List[Any]: The preprocessed list of arguments.
        """

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
        """
        Log an informational message.

        Args:
            msg (str): The message to be logged.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        args = self.__preprocess_args__(args)
        self.__logger.info(msg, *args, **kwargs)

    # ....................... #

    def error(self, msg: str, *args, **kwargs):
        """
        Log an error message.

        Args:
            msg (str): The error message to be logged.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        args = self.__preprocess_args__(args)
        self.__logger.error(msg, *args, **kwargs)

    # ....................... #

    def warning(self, msg: str, *args, **kwargs):
        """
        Log a warning message.

        Args:
            msg (str): The error message to be logged.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        args = self.__preprocess_args__(args)
        self.__logger.warning(msg, *args, **kwargs)

    # ....................... #

    def debug(self, msg: str, *args, **kwargs):
        """
        Log a debug message.

        Args:
            msg (str): The error message to be logged.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        args = self.__preprocess_args__(args)
        self.__logger.debug(msg, *args, **kwargs)

    # ....................... #

    def critical(self, msg: str, *args, **kwargs):
        """
        Log a critical message.

        Args:
            msg (str): The error message to be logged.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        args = self.__preprocess_args__(args)
        self.__logger.critical(msg, *args, **kwargs)
