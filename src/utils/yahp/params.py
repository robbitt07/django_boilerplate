from copy import deepcopy
from typing import Union


def parse_bool(val: Union[bool, str]) -> bool:
	"""
	Parse String or Boolean value to Boolean
	"""
	if isinstance(val, bool):
		return val
	if isinstance(val, str):
		if val in ('True', 'true'):
			return True
	return False



def get_if_int(d,k,default=None):
	"""
	Helper function to parse integers from a dictionary, primary for passing db keys when empty value may be ''
	"""
	v = str(d.get(k))
	if v.isdigit():
		return v
	return default

def parse_commas_sep_codes(val):
	"""
	Helper function to parse comma seperate parameters, typically for codes
	"""
	val_list = []
	if isinstance(val, str):
		if val != '':
			val_list = val.split(',')
	return val_list

def strip_dictionary_value_whitespace(d,force_str=False,inplace=True):
	"""
	Helper function to strip white space off dictionary values
	d = {
		'a' : ' this ',
		'b' : 'that ',
		'c' : None,
		'd' : 5
	}
	strip_dictionary_value_whitespace(d=d)
	strip_dictionary_value_whitespace(d=d,force_str=True)
	strip_dictionary_value_whitespace(d=d,inplace=False)
	"""
	if not inplace:
		d = deepcopy(d)
	if force_str:
		d.update({k : str(v).strip() for k,v in d.items()})
	else:
		d.update({k : v.strip() for k,v in d.items() if isinstance(v,str)})
	return d

def exclude_by_value(d,exclude_ls=[None,''],inplace=True):
	""" 
	Helper function to delete dictionary key-value pairs with specified values
	d = {
		'a' : '',
		'b' : None,
		'c' : 'c',
		'd' : 'de',
		'e' : 52
	}
	exclude_by_value(d)
	exclude_by_value(d,inplace=False)
	exclude_by_value(d,exclude_ls=[None])
	"""
	if not inplace:
		return {k : v for k,v in d.items() if not v in exclude_ls}
	exclude_keys = [k for k,v in d.items() if v in exclude_ls]
	for k in exclude_keys:
		del(d[k])
	return d


