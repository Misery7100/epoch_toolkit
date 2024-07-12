import os  # noqa: F401
from typing import Union

import sdf_helper as sdfh

from epoch_toolkit.core import (
    Unit,
)

from .file import FileHandler

# ----------------------- #


class FolderHandler(FileHandler):
    def __init__(
        self,
        unit: Union[str, Unit] = None,
        verbose: bool = False,
        log_level: str = "info",
        logger_name: str = "Folder Handler",
    ):
        super().__init__(
            unit=unit,
            verbose=verbose,
            log_level=log_level,
            logger_name=logger_name,
        )

    # ....................... #

    def read(self, folder: str):
        file_list = os.listdir(folder)
        file_list = list(filter(lambda x: x.endswith(".sdf"), file_list))
        file_list = list(map(lambda x: os.path.join(folder, x), file_list))

        for f in file_list:
            print(f, sdfh.get_job_id(f))
