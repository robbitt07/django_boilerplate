from django.utils import timezone

from datetime import datetime, date, time, timedelta
from dateutil.parser import parse as _dateutil_parse
from dateutil.relativedelta import relativedelta
from functools import lru_cache

import holidays
import pandas as pd
from typing import Set, Union
import pytz

UTC = pytz.timezone('UTC')


def get_this_week_start_end():
	dt = date.today()
	while dt.weekday() != 0:
		dt = dt - timedelta(days=1)
	start_datetime = datetime(
		year=dt.year,
		month=dt.month,
		day=dt.day,
		hour=0,
		minute=0,
		tzinfo=UTC,
	)
	end_datetime = start_datetime + timedelta(days=7)
	return start_datetime, end_datetime


def dateutil_parse(val: str) -> Union[datetime, date]:
	try:
		return _dateutil_parse(timestr=val)
	except:
		return ''


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
def historic_time(**kwargs) -> datetime:
    """Historic time based on now"""
    return timezone.now() - timedelta(**kwargs)


def historic_date(**kwargs) -> date:
    """Historic date based on now"""
    return timezone.now().date() - timedelta(**kwargs)


def future_time(**kwargs) -> datetime:
    """Future time based on now"""
    return timezone.now() + timedelta(**kwargs)


def future_date(**kwargs) -> date:
    """Future date at midnight"""
    return timezone.now().replace(hour=0, minute=0, second=0, microsecond=0).date() + timedelta(**kwargs)


def next_weekday(dt: datetime, weekday: int) -> datetime:
    """Get Next Weekday Occurence flowing provided datetime, 

    Parameters
    ----------
    dt : datetime
        Datetime 
    weekday : int
        # 0 = Monday, 1=Tuesday, 2=Wednesday...

    Returns
    -------
    datetime
        Next Weekday Occurrence
    """
    days_ahead = weekday - dt.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return dt + timedelta(days_ahead)


@lru_cache
def get_holidays(year: int) -> Set[date]:
    return {key for key in holidays.UnitedStates(years=year).keys()}


def today_is_holiday(date: date) -> bool:
    isHoliday = date in get_holidays(year=date.year)
    isWeekend = date.weekday() >= 5
    return isWeekend or isHoliday


def future_business_date(days: int, from_date: date = date.today()) -> date:
    business_days_to_add = days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        if today_is_holiday(current_date):
            continue
        business_days_to_add -= 1
    
    return current_date


def historical_business_date(days: int, from_date: date = date.today()) -> date:
    business_days_to_subtract = days
    current_date = from_date
    while business_days_to_subtract > 0:
        current_date -= timedelta(days=1)
        if today_is_holiday(current_date):
            continue
        business_days_to_subtract -= 1
    
    return current_date


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


def end_of_month(dt: date) -> date:
    """
    Get the end of a month from a Date or Datetime Object
    """
    if isinstance(dt, datetime):
        dt = dt.date().replace(day=1)

    if not isinstance(dt, date):
        raise ValueError(f"Must be `datetime.date` object, type={type(dt)}")

    return (dt + relativedelta(months=1)).replace(day=1) - timedelta(days=1)


def is_full_month(start: date, end: date) -> bool:
    """Check if Start and End Date make up a full month

    Parameters
    ----------
    start : date
        Start Date
    end : date
        End Date

    Returns
    -------
    bool
        Indicator if Start and End date make up full month
    """
    if is_same_month(start=start, end=end):
        return start == beginning_of_month(start) and end == end_of_month(start)
    
    return False


def is_same_month(start: date, end: date) -> bool:
    """Check if Start and End Date are same month

    Parameters
    ----------
    start : date
        Start Date
    end : date
        End Date

    Returns
    -------
    bool
        Indicator if Start and End are in same month
    """
    return start.year == end.year and start.month == end.month


def get_trailing_bom(lookback_months: int) -> list:
    """
    Get a trailing list of Beginning of Months for a requested lookback number of
    months
    """
    start_dt = beginning_of_current_month() - relativedelta(months=lookback_months)
    end_dt = beginning_of_current_month() - relativedelta(months=1)
    dates = pd.date_range(start_dt, end_dt, freq='MS')
    return list(dates.date)



def date_to_datetime(dt: date, start: bool = True, use_tz: bool = False) -> datetime:
    """
    Date to Timezone Aware Datetime
    
    start bool
        Indicator on either start or end of the day
    """
    # Get Current Timezone
    local_tz = timezone.get_current_timezone() if use_tz else timezone.UTC
    if start:
        # Datetime at beginning of the day
        return timezone.make_aware(
            timezone.datetime.combine(dt, datetime.min.time()), local_tz
        )

    # Datetime at end of the day
    return timezone.make_aware(
        timezone.datetime.combine(dt, datetime.max.time()), local_tz
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
			return val.strftime("%I:%M %p").lstrip("0")

		# Format for Date this year: Mar 3
		elif val.year == date.today().year:
			return f'{val.strftime("%b")} {val.day}'

		# Format for Date not this year: 10/8/22
		return f"{val.month}/{val.day}/{str(val.year)[2:4]}"

	elif isinstance(val, date):
		# Format Time for Today: Today
		if val == date.today():
			return "Today"

		# Format for Date this year: Mar 3
		elif val.year == date.today().year:
			return f'{val.strftime("%b")} {val.day}'

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
	if isinstance(val, str):
		if val != "":
			val = dateutil_parse(val=val)

	if isinstance(val, datetime):
		if val.tzinfo is not None:
			val = timezone.localtime(val)

		return f'{val.strftime("%b")} {val.day}, {str(val.year)[2:4]} {val.strftime("%I:%M %p").lstrip("0")}'

	elif isinstance(val, date):
		if val == date.today():
			return "Today"
		return f'{val.strftime("%b")} {val.day}, {str(val.year)[2:4]}'

	return val
