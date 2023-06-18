from django.http.request import QueryDict


def clean_query_params(query_params: dict, remove_blank: bool = False) -> dict:
    if query_params is None:
        return {}
    if isinstance(query_params, QueryDict):
        return {
            key: value for key, value in query_params.dict().items()
            if not (value == "" and remove_blank)
        }
    elif isinstance(query_params, dict):
        return {
            key: value for key, value in query_params.items()
            if not (value == "" and remove_blank)
        }
    return {}


def validate_int(val):
    try: 
        return int(val)
    except ValueError:
        return None
