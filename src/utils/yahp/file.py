from utils.yahp.datetime import UTC

from datetime import datetime
from logging import getLogger
import os

logger = getLogger("service")


def fl_last_update(fl: str) -> datetime:
    """File Last Update

    Parameters
    ----------
    fl : str
        _description_

    Returns
    -------
    datetime
        _description_
    """
    try:
        mtime = os.path.getmtime(fl)
    except OSError:
        logger.error(f"Unable to fetch datetiem for file", exc_info=True)
        mtime = 0

    return datetime.fromtimestamp(mtime, tz=UTC)
