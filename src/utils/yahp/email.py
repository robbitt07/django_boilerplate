from django.conf import settings

from products.yac.carrier.options import (
    DispatchContactRole, SafetyContactRole, OtherContactRole
)

import re
import requests
from typing import Dict, List


class TooManyRequests(Exception):
    pass


flag_words = [
    'accounting', 'office', 'contact', 'safety', 'claims', 'sales', 'compliance'
]


def normalize_email(email_address: str) -> str:
    if email_address is None:
        return email_address
    return str(email_address).split(' ')[0].lower().strip()


def get_email_classification(email_address: str) -> str:
    if '@' not in email_address:
        return None

    email_name = email_address.split('@')[0]
    if any(flag_word in email_name for flag_word in flag_words):
        return SafetyContactRole
    elif 'dispatch@' in email_address:
        return DispatchContactRole
    return OtherContactRole


def get_dispatch_email_or_first(email_ls: List[str]) -> str:
    if len(email_ls) == 0:
        return None
    for email in email_ls:
        if get_email_classification(email) == DispatchContactRole:
            return email
    return email_ls[0]


def generate_dispatch_email(email_address: str) -> bool:
    if email_address is None:
        return None
    if '@' not in email_address:
        return None
    domain = email_address.split('@')[1]
    return f"dispatch@{domain}"


def zero_bounce_email_validation(clean_email: str) -> Dict:
    response = requests.get(
        f"https://api.zerobounce.net/v2/validate",
        params={'email': clean_email, 'api_key': settings.ZERO_BOUNCE_API_KEY},
        timeout=(5, 30)
    )

    if response.status_code == 429:
        raise TooManyRequests()

    if response.status_code != 200:
        return {
            "email": clean_email,
            "valid": None,
            "error_code": "api",
            "error_desc": f"API Error | code={str(response.status_code)} reason={str(response.reason)}"
        }

    payload = response.json()
    if payload['status'] == "valid":
        return {
            "email": clean_email,
            "valid": True,
            "error_code": None,
            "error_desc": None,
            "extra": payload
        }
    elif payload['status'] == "invalid":
        return {
            "email": clean_email,
            "valid": False,
            "error_code": payload["sub_status"],
            "error_desc": "Invalid Email per Email Provider",
            "extra": payload
        }
    else:
        return {
            "email": clean_email,
            "valid": None,
            "error_code": payload["sub_status"],
            "error_desc": "Unable to Verify Email per Email Provider",
            "extra": payload
        }


def is_it_real_email_validation(clean_email: str) -> Dict:
    response = requests.get(
        "https://isitarealemail.com/api/email/validate",
        params={'email': clean_email},
        headers={'Authorization': f"Bearer {settings.IS_IT_REAL_EMAIL_API_KEY}"},
        timeout=(5, 30)
    )

    if response.status_code == 429:
        raise TooManyRequests()

    if response.status_code != 200:
        return {
            "email": clean_email,
            "valid": None,
            "error_code": "api",
            "error_desc": f"API Error | code={str(response.status_code)} reason={str(response.reason)}"
        }

    status = response.json()['status']
    if status == "valid":
        return {
            "email": clean_email,
            "valid": True,
            "error_code": None,
            "error_desc": None
        }
    elif status == "invalid":
        return {
            "email": clean_email,
            "valid": False,
            "error_code": "server",
            "error_desc": "Invalid Email per Email Provider"
        }
    else:
        return {
            "email": clean_email,
            "valid": None,
            "error_code": "unknown",
            "error_desc": "Unable to Verify Email per Email Provider"
        }


def validate_email(email_address: str,
                   check_mx: bool = True,
                   *args, **kwargs) -> Dict:
    """
    TODO: Switch out the Resource
     
    Helper Function to Validate Email.  Does not handle 403/401 errors with Authentication or Usage Errors

    Parameters
    -----------
        email str
            Email String
        check_mx bool
            Valdiate against MX API service
        api_key str
            Validation service API key 

    Returns
    -----------
        valid_email dict
            email str
                Normalized, lower stripped email address
            valid bool
                Indicator if clean email is valid
            error_code str optional
                Sting code of if validation fails
            error str optional
                Readable string of reason validation fails

    Reference 
    -----------
        https://docs.isitarealemail.com/how-to-validate-email-addresses-in-python
    """
    # Use Regex Validation First
    clean_email = normalize_email(email_address=email_address)
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not email_regex.match(clean_email):
        return {
            "email": clean_email, "valid": False, "error_code": "regex", "error_desc": "Invalid Format"
        }

    # Validate Email against MX domain check
    if check_mx:
        if settings.IS_IT_REAL_EMAIL_API_KEY != "":
            return is_it_real_email_validation(clean_email=clean_email)
        
        elif settings.ZERO_BOUNCE_API_KEY != "":
            return zero_bounce_email_validation(clean_email=clean_email)
        
        # Default if no email verification is configured
        return {
            "email": clean_email,
            "valid": True,
            "error_code": None,
            "error_desc": None
        }
    
    else:
        return {
            "email": clean_email,
            "valid": True,
            "error_code": None,
            "error_desc": None
        }


