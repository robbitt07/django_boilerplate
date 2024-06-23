from django.utils import timezone

from datetime import datetime, date, time, timedelta
from dateutil.parser import parse as _dateutil_parse
from dateutil.relativedelta import relativedelta

import pandas as pd
from typing import Union


def dateutil_parse(val: str) -> Union[datetime, date]:
	try:
		return _dateutil_parse(timestr=val)
	except:
		return ""


def is_outside_business_hours() -> bool:
    dt = datetime.now()
    # Day of Week
    dow = dt.weekday()
    if dow < 5 and dt.hour > 6 and dt.hour < 18:
        return True
    return False


def get_datetime_from_fields(date_field, time_field, default_time: time = time(12+4, 0, 0)):
    """
    Combine date fields and time fields into datetime object with TZ aware to server
    """
    if date_field is None:
        return None
    return datetime.combine(
        date_field,
        time_field or default_time,
        timezone.get_current_timezone()
    )


# TODO: Update to Historical Date/Datetime (Date and Datetime Objects)
def historic_time(**kwargs):
    """Historic time based on now"""
    return timezone.now() - timedelta(**kwargs)


def historic_date(**kwargs):
    """Historic date based on now"""
    return timezone.now().date() - timedelta(**kwargs)


def future_time(**kwargs):
    """Future time based on now"""
    return timezone.now() + timedelta(**kwargs)


def future_date(**kwargs):
    """Future date at midnight"""
    return timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(**kwargs)


def beginning_of_current_month() -> date:
    """
    Get the Start of the Current Month
    """
    return date.today().replace(day=1)


def beginning_of_month(dt: Union[datetime, date]) -> date:
    """
    Get the start of a month from a Date or Datetime Object
    """
    if isinstance(dt, datetime):
        return dt.date().replace(day=1)
    elif isinstance(dt, date):
        return dt.replace(day=1)
    raise ValueError("Must be of type date or datetime")


def get_trailing_bom(lookback_months: int) -> list:
    """
    Get a trailing list of Beginning of Months for a requested lookback number of
    months
    """
    start_dt = beginning_of_current_month() - relativedelta(months=lookback_months)
    end_dt = beginning_of_current_month() - relativedelta(months=1)
    dates = pd.date_range(start_dt, end_dt, freq="MS")
    return list(dates.date)


def date_to_tz_datetime(dt: date, start: bool = True) -> datetime:
    """
    Date to Timezone Aware Datetime
    
    start bool
        Indicator on either start or end of the day
    """
    # Get Current Timezone
    local_tz = timezone.get_current_timezone()
    if start:
        # Datetime at beginning of the day
        return timezone.make_aware(
            timezone.datetime.combine(dt, datetime.min.time()), local_tz
        )
    # Datetime at end of the day
    return timezone.make_aware(
        timezone.datetime.combine(dt, datetime.min.time()), local_tz
    )


def between_datetimes(dt: datetime, start: datetime, end: datetime):
    """
    Helper Function to Check if Value is Between Optionall None Start and End
    """
    if dt is None:
        return True

    if start is None:
        # Check if time is Less than Initial Period End
        if dt <= end:
            return True
        return False
    elif end is None:
        # Check if time is After Final Period Start
        if dt >= start:
            return True
        return False

    # Check if Value Between 
    return start <= dt < end


def get_short_datetime_display(val: Union[datetime, date, str], force_date: bool = False) -> str:
	"""
	Clean Short Datetime for Elements for fields like Pickup On, Create On or Updated On. 
	Ideal for lists.

	3:40pm
	10:00am 
	Mar 3
	Jan 2
	10/8/22
	"""
	if isinstance(val, str):
		val = dateutil_parse(val=val)

	if isinstance(val, datetime):
		if val.tzinfo is not None:
			val = timezone.localtime(val)

		# Format Time for Today: 10:00am
		if val.date() == date.today() and not force_date:
			return val.strftime('%I:%M %p').lstrip("0")

		# Format for Date this year: Mar 3
		elif val.year == date.today().year:
			return f"{val.strftime('%b')} {val.day}"

		# Format for Date not this year: 10/8/22
		return f"{val.month}/{val.day}/{str(val.year)[2:4]}"

	elif isinstance(val, date):
		# Format Time for Today: Today
		if val == date.today():
			return "Today"

		# Format for Date this year: Mar 3
		elif val.year == date.today().year:
			return f"{val.strftime('%b')} {val.day}"

		# Format for Date not this year: 10/8/22
		return f"{val.month}/{val.day}/{str(val.year)[2:4]}"

	return val


def get_long_datetime_display(val: Union[datetime, date, str]) -> str:
	"""
	Clean Long Datetime for Elements for fields like Pickup On, Create On or Updated On. 
	Ideal for DetaiL Pages.

	3:40pm
	10:00am
	Mar 3 3:40pm
	Jan 2 10:00am
	10/8/22 8:30pm
	"""
	if pd.isnull(val):
		return ""

	if isinstance(val, str):
		if val != "":
			val = dateutil_parse(val=val)

	if isinstance(val, datetime):
		if val.tzinfo is not None:
			val = timezone.localtime(val)

		return f"{val.strftime('%b')} {val.day}, {str(val.year)[2:4]} {val.strftime('%I:%M %p').lstrip('0')}"

	elif isinstance(val, date):
		if val == date.today():
			return "Today"
		return f"{val.strftime('%b')} {val.day}, {str(val.year)[2:4]}"

	return val