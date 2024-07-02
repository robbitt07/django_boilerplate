from typing import Any, Dict, List, Optional, Tuple, Union


def get_embedded_value(obj: Union[Dict, object], keys: List):
    """Get Object from Object where Key Embedding is a List"""
    for key in keys:
        try:
            if isinstance(obj, Dict):
                obj = obj[key]
            else:
                obj = getattr(obj, key)
        except (KeyError, AttributeError):
            return None

    return obj


def get_value(obj: Union[Dict, object], key: str):
    """Get Value from Object, Dictionary, embedded or simple"""

    # Get Embedded Value
    if '.' in key:
        keys = key.split('.')
        return get_embedded_value(obj, keys)

    if isinstance(obj, Dict):
        return obj.get(key)

    return getattr(obj, key, None)


def equal(a: Any, b: Any) -> bool:
    return a == b


def not_equal(a: Any, b: Any) -> bool:
    return a != b


def gt(a: Any, b: Any) -> bool:
    return a > b


def lt(a: Any, b: Any) -> bool:
    return a < b


def gte(a: Any, b: Any) -> bool:
    return a >= b


def lte(a: Any, b: Any) -> bool:
    return a <= b


def contains(a: Any, b: Any) -> bool:
    return a in b


def not_contains(a: Any, b: Any) -> bool:
    return a not in b


operator_map = {
    None: equal,
    "not": not_equal,
    "gt": gt,
    "lt": lt,
    "gte": gte,
    "lte": lte,
    "in": contains,
    "not_in": not_contains
}


def get_operator(filter_key: Optional[str] = None) -> Tuple[str, callable]:
    """Get Operator"""
    if filter_key is None:
        return filter_key, operator_map[None]

    split_filter_key = filter_key.split("__")

    assert len(split_filter_key) in (1, 2,), "Strings can only contain single operator"

    if len(split_filter_key) == 1:
        return filter_key, operator_map[None]

    filter_key, operator_key = split_filter_key

    assert operator_key in operator_map, f"`{operator_key}` not valid operator"

    return filter_key, operator_map[operator_key]


def apply_filter(obj: Union[Any, Dict], filter_value: Any, filter_key: Optional[str] = None) -> bool:
    """Apply Filter to an Object"""
    filter_key, operator = get_operator(filter_key)

    # Get Value
    if filter_key is None:
        value = obj
    else:
        value = get_value(obj, filter_key)

    return operator(value, filter_value)


def apply_filters(obj: Union[Any, Dict], filters: Optional[Dict] = None) -> bool:
    """Apply Filters to Object Payload"""
    # No Need to Filter if no filters applied
    if filters is None:
        return True

    # Apply Filters
    return all(
        apply_filter(obj=obj, filter_value=filter_value, filter_key=filter_key)
        for filter_key, filter_value in filters.items()
    )


def filter_list(arr: List[Union[object, Dict]],
                filters: Optional[Dict] = None) -> List[Union[object, Dict]]:
    """Filter List of Objects

    Parameters
    ----------
    arr : List[Union[object, Dict]]
        List or Array of Objects to Filter
    filters : Optional[Dict], optional
        Filters, by default None

    Returns
    -------
    List[Union[object, Dict]]
        Filtered List of Objects
    """

    return [obj for obj in arr if apply_filters(obj=obj, filters=filters)]


def agg_list(arr: List[Union[object, Dict]],
             field: str,
             func: callable,
             filters: Optional[Dict] = None) -> Any:
    """Aggregate List of Objects, apply filter if available

    Parameters
    ----------
    arr : List[Union[object, Dict]]
        Array of Objects to Filter and Aggregate
    field : str
        Field to Aggregate On
    func : callable
        Function to Aggregate
    filters : Optional[Dict], optional
        Dictionary of Filters to Apply to List, by default None

    Returns
    -------
    Any
        Aggregated Value
    """

    filtered_arr = filter_list(arr=arr, filters=filters)

    return func(get_value(obj, field) for obj in filtered_arr)


def get_prefix_dict(obj: Dict, prefix: str, prefix_only: bool = True) -> Dict:
    """Get Prefix dictionary, filter and extract base values

    Parameters
    ----------
    obj : Dict
        Dictionary of Items
    prefix : str
        String Prefix to Filter and Replace, i.e. "origin_"
    prefix_only: bool, default True
        Indicator to filter out items that do not start with prefix
 
    Returns
    -------
    Dict
        Filtered and Transformed Dictionary
    """
    if prefix_only:
        return {
            key.replace(prefix, ""): value for key, value in obj.items()
            if key.startswith(prefix)
        }

    return {
        key.replace(prefix, ""): value for key, value in obj.items()
    }


def any_none(*args: Any) -> bool:
    """Any items in array are None

    Returns
    -------
    bool
        Indicator if Any Items are None
    """
    return any([val is None for val in args])


def all_none(*args: Any) -> bool:
    """All items in array are None

    Returns
    -------
    bool
        Indicator if All Items are None
    """
    return all([val is None for val in args])
