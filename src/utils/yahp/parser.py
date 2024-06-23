
from typing import List
import django
from django.utils import timezone

import datetime
import numpy as np
import pandas as pd
import pytz
import re


def list_remove_none(ls : List):
	"""
	Remove None Values from List
	"""
	return [x for x in ls if pd.notna(x)] or None

def list_apply_to_non_none(ls : List, func : callable):
	"""
	Apply a Function to Provided List with None Values Removed

	returns func(lst with Nones removed)
	"""
	ls = list_remove_none(ls=ls)
	if ls is None:
		return None
	return func(ls)


def numeric_regex_sub(x): return re.sub("[^0-9.-]+", "", x)


def remove_list_na(ls: List):
	"""Remove NA Values from a List"""
	return [x for x in ls if pd.notna(x)]


def none_if_empty(ls: List, func: callable):
	"""Return None if List is Empty"""
	if len(ls) == 0:
		return None
	return func(ls)


def unravel_list(ls):
	"""Unravel List of Lists"""
	return [x for sub_ls in ls for x in sub_ls]


def parse_varchar(x, nullable=True, default=""):
	"""
	Test Cases
	----------
        parse_varchar("this")
        parse_varchar("THAT")
        parse_varchar(12.5)
        parse_varchar(15659)
        parse_varchar(None)
	"""
	if isinstance(x, str):
		return x
	if pd.isna(x):
		if nullable:
			return None
		return default
	return str(x)


def parse_numeric(x, nullable=True, default=0, alpha_strict=False):
	"""
	Test Cases
	----------
        parse_numeric(23)
        parse_numeric("23")
        parse_numeric(np.int32(23))
        parse_numeric(np.float32(23.1))
        parse_numeric(23.2)
        parse_numeric("23.2")
	"""
	if pd.isna(x):
		if nullable:
			return None
		return default
	if isinstance(x, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
		return float(x)
	if isinstance(x, str):
		if not alpha_strict:
			x = numeric_regex_sub(x)
		try:
			return float(x)
		except:
			if nullable:
				return None
			return default
	try:
		return float(x)
	except:
		if nullable:
			return None
		return default


def parse_integer(x, nullable=True, default=0):
	"""
	Test Cases
	----------
        parse_integer(23)
        parse_integer("23")
        parse_integer(np.int32(23))
        parse_integer(np.float32(23.1))
        parse_integer(23.2)
        parse_integer("23.2")
	"""
	if pd.isna(x):
		if nullable:
			return None
		return default
	if isinstance(x, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
		return int(x)
	if isinstance(x, str):
		x = parse_numeric(x)
		try:
			return int(x)
		except:
			if nullable:
				return None
			return default
	try:
		return int(x)
	except:
		if nullable:
			return None
		return default


def parse_bool(x, nullable=True, default=False):
	"""
	Test Cases
	----------
		parse_bool(True)
		parse_bool(False)
		parse_bool("True")
		parse_bool("False")
		parse_bool("TRUE")
		parse_bool("FALSE")
		parse_bool("T")
		parse_bool("t")
		parse_bool("F")
		parse_bool("f")
		parse_bool("Y")
		parse_bool("y")
		parse_bool("1")
		parse_bool("yes")
		parse_bool("Yes")
		parse_bool("YES")
		parse_bool("n")
		parse_bool("N")
		parse_bool("no")
		parse_bool("No")
		parse_bool("NO")
		parse_bool("0")
	"""
	if isinstance(x, bool):
		return x
	if isinstance(x, (int, np.int8, np.int16, np.int32, np.int64)):
		x = int(x)
		return x > 0
	if isinstance(x, (float, np.float16, np.float32, np.float64)):
		x = float(x)
		return x > 0
	if isinstance(x, str):
		if x.lower() in ["yes", "y", "true", "t", "1"]:
			return True
		if x.lower() in ["no", "n", "false", "f", "0"]:
			return False
	if nullable:
		return None
	return default


def required_parse_bool(x, default=False):
	return parse_bool(x=x, nullable=False, default=default)


def try_parsing_date(x: str) -> datetime.datetime:
	"""
	String to Datetime parser with default Pandas parser then secondary know suboptimal formats
	"""
	if x.isnumeric() and len(x) == 5:
		x = x.zfill(6)

	if x.isnumeric() and len(x) == 7:
		x = x.zfill(8)
	try:
		return pd.to_datetime(x).to_pydatetime()
	except:
		for fmt in ("%m%d%y", "%m%d%Y", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
			try:
				return datetime.datetime.strptime(x, fmt)
			except ValueError:
				pass
		raise ValueError("no valid date format found")


def parse_date(x,
               nullable: bool = True,
               default: datetime.datetime = None,
               local_tz: bool = False):
	"""
	Test Cases
	----------
		parse_date("2020-11-01")
		parse_date("2020/11/01")
		parse_date("2020-11-01 12:00")
		parse_date("2020-11-1")
		parse_date("11-1-2020")
		parse_date("11/1/2020")
		parse_date("72121") # 7/21/21
		parse_date("103021") # 10/30/21
		parse_date("12521") # 1/25/21
		parse_date("1252021") # 1/25/21
		parse_date("12052021") # 12/25/21
		parse_date(datetime.datetime.now())
		parse_date(datetime.date.today())
	"""
	if not isinstance(x, (str, datetime.datetime, datetime.date)):
		x = str(x)

	try:
		dt = try_parsing_date(x)
		# Make Timezone Aware if not already
		if dt.tzinfo is None:
			dt = timezone.make_aware(dt, pytz.timezone("UTC"))
		elif local_tz:
			dt = dt.astimezone(timezone.get_current_timezone())
		return dt.date()
	except:
		if nullable:
			return None
		elif default is None:
			default = timezone.now().date()
		return default


def parse_datetime(x,
                   nullable: bool = True,
                   default: datetime.datetime = None,
                   local_tz: bool = False):
	"""
	Test Cases
	----------
		parse_date("2020-11-01")
		parse_date("2020/11/01")
		parse_date("2020-11-01 12:00")
		parse_date("2020-11-1")
		parse_date("11-1-2020")
		parse_date("11/1/2020")
		parse_date("72121") # 7/21/21
		parse_date("103021") # 10/30/21
		parse_date("12521") # 1/25/21
		parse_date("1252021") # 1/25/21
		parse_date("12052021") # 12/25/21
		parse_date(datetime.datetime.now())
		parse_date(datetime.date.today())
	"""
	if not isinstance(x, (str, datetime.datetime, datetime.date)):
		x = str(x)

	try:
		# TODO: Update Try Parsing Datetime function
		dt = try_parsing_date(x)
		# Make Timezone Aware if not already
		if local_tz:
			dt = dt.replace(tzinfo=None).astimezone(timezone.get_current_timezone())
		elif dt.tzinfo is None:
			dt = timezone.make_aware(dt, pytz.timezone("UTC"))
		return dt
	except:
		if nullable:
			return None
		elif default is None:
			default = timezone.now()
		return default


def parse_time(x, nullable=True, default=None):
	"""
	Test Cases
	----------
		parse_time("2020-11-01")
		parse_time("2020/11/01 4:00 PM")
		parse_time("2020/11/01 4 PM")
		parse_time("2020-11-01 12:00")
		parse_time("2020-11-1 13:31")
		parse_time("11-1-2020")
		parse_time("11/1/2020")
		parse_date("72121")
		parse_date("103021")
		parse_time(datetime.datetime.now())
		parse_time(datetime.date.today())
	"""
	if not isinstance(x, (str, datetime.datetime, datetime.date, datetime.time)):
		x = str(x)

	try:
		dt = try_parsing_date(x)
		dt = timezone.make_aware(dt, pytz.timezone("UTC"))
		return dt.time()
	except:
		if nullable:
			return None
		elif default is None:
			default = timezone.now().time()
		return default


FIELD_CLEANING_ROUTER = {
	django.db.models.fields.CharField.__name__ : parse_varchar,
	django.db.models.fields.TextField.__name__ : parse_varchar,
	django.db.models.fields.DecimalField.__name__ : parse_numeric,
	django.db.models.fields.IntegerField.__name__ : parse_integer,
	django.db.models.fields.NullBooleanField.__name__ : parse_bool,
	django.db.models.fields.BooleanField.__name__ : required_parse_bool,
	django.db.models.fields.DateField.__name__ : parse_date,
	django.db.models.fields.TimeField.__name__ : parse_time,
	None : None,
}

def zip_code_regex_sub(z,nullable=True,default="unk",allow_aggregate_zip_code=False):
	"""
	Test Cases
	----------
		zip_code_regex_sub(54944.1)
		zip_code_regex_sub("54944.0")
		zip_code_regex_sub("1101")
		zip_code_regex_sub("54944-0110")
		zip_code_regex_sub("4944-0110")
	"""
	if pd.isna(z):
		if nullable:
			return None
		return default
	if isinstance(z, (int, float, np.int8, np.int16, np.int32, np.int64, np.float32, np.float64)):
		z = parse_integer(z)
	if not isinstance(z,str):
		z = str(z)
	if "." in z:
		z = z.split(".")[0]
	if "-" in z:
		z = z.split("-")[0]
	z = re.sub("[^0-9a-zA-Z-]+","",z)
	if z.isnumeric():
		if allow_aggregate_zip_code:
			if len(z) <= 3:
				return z.zfill(3)
			return z.zfill(5)[:5]
		else:
			return z.zfill(5)[:5]
	return z.upper()


def check_handle_numeric_precision(x,max_digits,decimal_places,on_size_error="set_none",on_precision_error="coerce"):
	"""
	Validate Numerical Values Are Appropriate for Decimal Data Types

	Parameters
	-----------
	x : float
		Numeric value
	max_digits : int 
		Max digits for decimal field
	decimal_places : int 
		Max number of decimal places for decimal field
	on_size_error : str
		How to handle max_digit violation: "set_none", "coerce", or "raise_error"
	on_precision_error : str
		How to handle decimal_places violation: "set_none", "coerce", or "raise_error"
	
	Returns
	-----------
	x : float
		Decimal value
	violates_max_digits : bool
		x violates max_digits constraint
	violates_decimal_places : bool
		x violates decimal_places_contraint
	"""
	violates_max_digits = None
	violates_decimal_places = None
	if pd.isna(x):
		return None,violates_max_digits,violates_decimal_places
	upper_bound = 10 ** (max_digits-decimal_places)
	if int(np.abs(x)/upper_bound) != 0:
		# x violated max_digits
		violates_max_digits = True
		if on_size_error == "coerce":
			x = upper_bound - 1 / 10 ** decimal_places
		elif on_size_error == "set_none":
			return None,violates_max_digits,violates_decimal_places
		else:
			raise ValueError(f"Invalid value {x} for max_digits {max_digits}, decimal_places {decimal_places}")
	else:
		violates_max_digits = False
	if x != round(x,4):
		# x violated decimal_places
		violates_decimal_places = True
		if on_precision_error == "coerce":
			x = round(x,4)
		elif on_precision_error == "set_none":
			return None,violates_max_digits,violates_decimal_places
		else:
			raise ValueError(f"Invalid value {x} for max_digits {max_digits}, decimal_places {decimal_places}")
	else:
		violates_decimal_places = False
	return x,violates_max_digits,violates_decimal_places
