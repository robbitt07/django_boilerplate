
from typing import Any, List, Union


def get_first_list_el(ls: List) -> Union[None, Any]:
    if len(ls) >= 1:
        return ls[0]
    return None


def chunks(data, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(data), n):
        yield data[i:i + n]
