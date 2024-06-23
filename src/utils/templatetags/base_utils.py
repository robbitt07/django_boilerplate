from django import template

from utils.yahp.strings import code_to_display as code_to_display_func, get_offuscate_number
from utils.yahp.parser import parse_numeric
from utils.yahp.phone_number import PhoneNumber
from utils.yahp.datetime import (
	dateutil_parse, get_long_datetime_display, get_short_datetime_display
)

from datetime import datetime, date
from decimal import Decimal
from typing import Any, Union

register = template.Library()


@register.filter
def code_to_display(val):
	"""
	Convert Code to Display `lane_valid_till` -> Lane Valid Till
	"""
	try:
		return code_to_display_func(val)
	except Exception:
		# Model does not have method get_absolute_url
		return None


@register.filter(name='phone')
def format_phone(phone_number):
	if not phone_number:
		return ''
	elif not isinstance(phone_number, PhoneNumber):
		phone_number = PhoneNumber(phone_number)
	return str(phone_number)


@register.filter
def subtract(x, y):
	try:
		return x-y
	except:
		try:
			x = float(x)
			y = float(y)
			return x-y
		except:
			return None


@register.filter
def divide(x, y):
	try:
		return x / y
	except:
		try:
			x = float(x)
			y = float(y)
			return x / y
		except:
			return None


@register.filter
def keyvalue(d, k):
	return d.get(k)


@register.filter
def zip_(a, b):
	return zip(a, b)


@register.filter
def trending_display(val):
	"""
	Provide either Thrending Arrow Display
	TODO: Handle mangitude of trending, $5 on $25k is less significant than $50k
	"""
	val_display = ""
	val_parsed = parse_numeric(val)
	if val is None or isinstance(val, str):
		return ''
	if val_parsed is not None:
		val_display = "{:10.1f}".format(val_parsed)
	if val > 0:
		return f'<i class="fas fa-arrow-up icon-positive" title="{val_display}">'
	elif val < 0:
		return f'<i class="fas fa-arrow-down icon-negative" title="{val_display}">'
	return ''


@register.filter
def queryset_order_by(qs, ordering):
	try:
		return qs.order_by(ordering)
	except:
		return qs


@register.filter
def queryset_filter(qs, args=''):
	arg_ls = args.split(',')
	if len(arg_ls) != 2:
		return qs
	k, v = arg_ls
	try:
		return qs.filter(**{k: v})
	except:
		return qs


@register.filter
def replace(value, arg):
	"""
	Replacing filter
	Use `{{ "aaa"|replace:"a|b" }}`
	"""
	if len(arg.split('|')) != 2:
		return value

	what, to = arg.split('|')
	return value.replace(what, to)


@register.filter
def parse_date_str(val):
	"""
	Parse Datetime String to Datetime Object
	"""
	return dateutil_parse(val=val)


@register.filter
def list_reverse(val):
	"""
	Reverse the ordering of an iterable object
	"""
	try:
		return list(val)[::-1]
	except:
		return []


@register.filter
def list_element(val, idx):
	"""
	Return list element
	"""
	try:
		return list(val)[int(idx)]
	except:
		return None


def json_display_recursion(obj, html='', depth=0, max_depth=10, max_obj_len=15):
	depth += 1
	html = '\n'.join(
		[html, '<table class="table table-hover table-sm" id="dataTable">'])
	if not isinstance(obj, (dict, list,)) or depth >= max_depth:
		return f'{obj:,}' if isinstance(obj, int) else str(obj)
	elif isinstance(obj, dict):
		cnt = 0
		for k, v in obj.items():
			cnt += 1
			if cnt > max_obj_len:
				break
			sub_html = json_display_recursion(
				obj=v,
				depth=depth,
				max_depth=max_depth,
				max_obj_len=max_obj_len
			)
			html = '\n'.join(
				[html, f'<tr class="text-center">\n<td>{k}</td>\n<td>{sub_html}</td></tr>'])
		if len(obj) > max_obj_len:
			html = '\n'.join(
				[html, f'<tr class="text-center">\n<td>{len(obj)-max_obj_len} Remaining...</td></tr>'])
	elif isinstance(obj, list):
		html = '\n'.join([html, f'<tr class="text-center">'])
		for v in obj[:max_obj_len]:
			sub_html = json_display_recursion(
				obj=v,
				depth=depth,
				max_depth=max_depth,
				max_obj_len=max_obj_len
			)
			html = '\n'.join([html, f'<td>{sub_html}</td>'])
		if len(obj) > max_obj_len:
			html = '\n'.join(
				[html, f'<tr class="text-center">\n<td>{len(obj)-max_obj_len} Remaining...</td></tr>'])
		html = '\n'.join([html, f'</tr>'])
	html = '\n'.join([html, '</table>'])
	return html


@register.filter
def json_display(obj, arg_str=None):
	max_depth = None
	max_obj_len = None
	if arg_str is not None:
		try:
			max_depth, max_obj_len = arg_str.split(',')
			max_depth = int(max_depth)
			max_obj_len = int(max_obj_len)
			assert max_depth > 0
			assert max_obj_len > 0
		except:
			pass
	try:
		kwargs = {'obj': obj}
		if max_depth is not None:
			kwargs.update({'max_depth': max_depth})
		if max_obj_len is not None:
			kwargs.update({'max_depth': max_obj_len})
		return json_display_recursion(**kwargs)
	except Exception:
		return None


@register.filter
def short_datetime(val: Union[datetime, date, str]) -> str:
	"""
	Clean Short Datetime for Elements for fields like Pickup On, Create On or Updated On. 
	Ideal for lists.

	3:40pm
	10:00am 
	Mar 3
	Jan 2
	10/8/22
	"""
	return get_short_datetime_display(val=val)


@register.filter
def long_datetime(val: Union[datetime, date, str]) -> str:
	"""
	Clean Long Datetime for Elements for fields like Pickup On, Create On or Updated On. 
	Ideal for DetaiL Pages.

	3:40pm
	10:00am
	Mar 3 3:40pm
	Jan 2 10:00am
	10/8/22 8:30pm
	"""

	return get_long_datetime_display(val=val)


@register.filter
def offuscate(val: Union[str, int]) -> str:
	if val is None or val == "":
		return val
	return get_offuscate_number(val, 4)



@register.filter
def currency(value: Any, decimal_places: int = 2) -> str:
	try:
		decimal_places = int(decimal_places)
	except:
		decimal_places = 2
	try:
		if value is None:
			return ''
		if isinstance(value,str):
			if value == '':
				return ''
			else:
				value = float(value)
		
		value = float(value)
		currency_formatter = r'{:,.' + str(decimal_places) + r'f}'
		if round(value,decimal_places) > 0:
			return '$' + currency_formatter.format(value)
		elif round(value,decimal_places) < 0:
			return '-$' + currency_formatter.format(-value)
		else:
			return '$0.00'
	except:
		return ''


@register.filter
def int_currency(value):
	try:
		if value is None:
			return ''
		if isinstance(value, str):
			if value == '':
				return ''
			else:
				value = float(value)
		currency_formatter = r'{:,.0f}'
		if round(value, 0) > 0:
			return '$' + currency_formatter.format(value)
		elif round(value, 0) < 0:
			return '-$' + currency_formatter.format(-value)
		else:
			return '$0'
	except:
		return ''

@register.filter
def large_currency(value):
	try:
		if value is None:
			return ''
		if isinstance(value, str):
			if value == '':
				return ''
			else:
				value = float(value)
		if value >= 100000000000:
			return f'${round(value/10**9):,}BB'
		elif value > 999999999:
			return f'${round(value/10**9,1):,}BB'
		elif value >= 100000000:
			return f'${round(value/10**6):,}MM'
		elif value > 999999:
			return f'${round(value/10**6,1):,}MM'
		elif value >= 100000:
			return f'${round(value/10**3):,}K'
		elif value > 999:
			return f'${round(value/10**3,1):,}K'
		else:
			return f'${round(value):,}'
	except:
		return ''


@register.filter
def percent(value: Any, decimal_places: int = 0) -> str:
	try:
		if value is None:
			return ''
		if isinstance(value, str):
			if value == '':
				return ''
			else:
				value = float(value)
		percent_formatter = r'{:,.' + str(decimal_places) + r'f}'
		return percent_formatter.format(100*value) + '%'
	except:
		return ''


