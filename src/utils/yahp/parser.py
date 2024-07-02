from django.utils import timezone

from datetime import datetime, date
import pytz
import pandas as pd
import numpy as np
import re
from typing import Any, List, Optional, Union

# TODO: Move to datetime
LOCAL_TZ_KEY = timezone.get_current_timezone().key
LOCAL_TZ = pytz.timezone(LOCAL_TZ_KEY)


def localize_dt(dt: datetime) -> datetime:
	return LOCAL_TZ.localize(dt=dt)


def numeric_regex_sub(x): return re.sub("[^0-9.-]+", "", x)


def parse_bool(val: Union[bool, str],
               allow_none: bool = True,
               true_values: set = {"true", "yes", "y"}) -> bool:
	"""
	Parse String or Boolean value to Boolean
	"""
	if val is None and allow_none:
		return None

	if isinstance(val, bool):
		return val
	
	if isinstance(val, str):
		val = val.lower().strip()
		if val in true_values:
			return True

	return False


def parse_numeric(x,
                  nullable: bool = True,
                  default: float = 0.0,
                  alpha_strict: bool = False):
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


def parse_integer(x, nullable: bool = True, default: int = 0) -> Optional[int]:
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


def try_parsing_date(x: str) -> datetime:
	"""
	String to Datetime parser with default Pandas parser then secondary know suboptimal formats
	"""
	if x is None:
		return None

	if x.isnumeric() and len(x) == 5:
		x = x.zfill(6)

	if x.isnumeric() and len(x) == 7:
		x = x.zfill(8)
	try:
		return pd.to_datetime(x).to_pydatetime()
	except:
		fmts = (
			"%m/%d/%Y %H:%M:%S:%f", "%m/%d/%Y %H:%M:%S", "%m%d%y", "%m%d%Y",
			"%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"
		)
		for fmt in fmts:
			try:
				return datetime.strptime(x, fmt)
			except ValueError:
				pass
		raise ValueError(f"no valid date format found={x}")


def parse_date(x, nullable: bool = True, default: datetime = None):
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
	if not isinstance(x, (str, datetime, date)):
		x = str(x)

	try:
		dt = try_parsing_date(x)
		# Make Timezone Aware if not already
		if dt.tzinfo is None:
			dt = timezone.make_aware(dt, pytz.timezone("UTC"))
		return dt.date()
	except:
		if nullable:
			return None
		elif default is None:
			default = timezone.now().date()
		return default


def parse_datetime(x,
				   nullable: bool = True,
				   default: datetime = None,
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
	if not isinstance(x, (str, datetime, date)):
		x = str(x)

	try:
		# TODO: Update Try Parsing Datetime function
		dt = try_parsing_date(x)
		# Make Timezone Aware if not already
		if local_tz:
			dt = LOCAL_TZ.localize(dt)
		elif dt.tzinfo is None:
			dt = timezone.make_aware(dt, pytz.timezone("UTC"))
		return dt
	
	except Exception as e:
		print(str(e))
		if nullable:
			return None
		elif default is None:
			default = timezone.now()
		return default


def parse_date_and_time(date_str: str, time_str: str, local_tz: bool = False) -> datetime:
	if date_str is None:
		return None
	try:
		date_obj = pd.to_datetime(date_str)
		if date_obj is None:
			return None
		date_obj = date_obj.date()
		time_obj = datetime.strptime(str(time_str or "").zfill(6), "%H%M%S").time()

		dt_obj = datetime.combine(date_obj, time_obj)
		if local_tz and dt_obj is not None:
			dt_obj = LOCAL_TZ.localize(dt_obj)

		return dt_obj
	except:
		print(date_str, time_str)


def parse_array(val: str,
				sep: str = ",",
				parser: Optional[callable] = lambda x: x) -> List[Any]:
	"""Parse Array

	Parameters
	----------
	val : str
		_description_
	sep : str, optional
		_description_, by default ","
	parser : _type_, optional
		_description_, by default lambdax:x

	Returns
	-------
	List[Any]
		_description_
	"""
	return [parser(sub) for sub in val.split(sep)]


def parse_list_integer(val: Any, sep: str = ",") -> List[int]:
	"""Parse List of Interger

	Parameters
	----------
	val : Any
		Parameter Value
	sep : str, optional
		Seperator for spliting to list, by default ","

	Returns
	-------
	List[int]
		List of Integers 
	"""
	return parse_array(val=val, parser=parse_integer, sep=sep)
