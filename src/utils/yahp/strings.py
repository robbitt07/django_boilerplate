from functools import lru_cache
import random
import re
import string


@lru_cache(maxsize=1000)
def string_to_html(val: str) -> str:
    """
    Helper function to convert string with new lines, tabs and spaces to safe html
    string
    """
    if val is None:
        return ""
    val = val.strip().replace("\n", "<br>")
    val = val.replace("\t", "&emsp;")
    val = val.replace("    ", "&emsp;").replace("  ", "&ensp;")
    return val


def generate_random_slug(k: int = 10) -> str:
    return ''.join(random.choices(
        string.ascii_uppercase + string.ascii_lowercase + string.digits, k=k
    ))


@lru_cache(maxsize=1000)
def normalize_entity_string(val: str) -> str:
    val = str(val).strip()
    val = re.sub(r'[^A-Za-z0-9]+', ' ', val)
    return re.sub(' +', ' ', val)


def truncate_string(val, max_length=30):
    if len(val) > max_length:
        return f'{val[0:max_length]}...'
    return val


def code_to_display(val, remove_id=False):
    """
    Convert Code to Display
    
    remove_id bool
        Removes `id` from the display, Carrier Id -> Carrier
    """
    val_ls = [
        x.title() for x in str(val).split('_') if not (x.lower() == 'id' and remove_id)
    ]
    return ' '.join(val_ls)


def slugify(val: str):
    val = re.sub(r'[^\w\s-]', '', val).strip().lower()
    return re.sub(r'[-\s]+', '-', val)


@lru_cache(maxsize=1000)
def slug_hash(val: str, max_len: int = 50, hash_len: int = 10):
    return f"{slugify(val)[0:max_len-hash_len-1]}-{generate_random_slug(hash_len)}"


def get_offuscate_number(val: str, digits_show: int = 4) -> str:
    return f"****{str(val)[-digits_show:]}"
