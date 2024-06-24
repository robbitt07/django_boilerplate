from datetime import datetime, date
from pandas import notna
from typing import Any, Dict, Tuple

DEFAULT_EXCLUDE = ['created_on', 'updated_on', 'created_by', 'updated_by']


def model_to_dict(instance,
                  fields: list = None,
                  exclude_id: bool = False,
                  exclude: list = None,
                  properties: list = None,
                  exclude_none: bool = False,
                  default_exclude: list = DEFAULT_EXCLUDE,
                  include_display: bool = False):
	'''
	Returns a dictionary object containing complete field-value pairs of the given instance

	Convertion rules:

		datetime.date --> str
		many_to_many --> list of id's

	'''
	if exclude is None:
		exclude = []

	# Exclude ID (Transfer Object -> Carrier Sync)
	if isinstance(exclude, Tuple):
		exclude = list(exclude)

	if exclude_id:
		exclude += ['id']
	# Get all Exclude Columns (Requested + Default )
	exclude += default_exclude
	# Concrete and m2m Fields
	concrete_fields = instance._meta.concrete_fields
	m2m_fields = instance._meta.many_to_many

	data = {}
	# Concrete Fields
	for field in concrete_fields:
		key = field.name
		# Check if in Fields (if valid)
		if fields is not None:
			if key not in fields:
				continue

		# Check for exclude
		if key in exclude:
			continue

		value = field.value_from_object(instance)

		# Exclude None where Requested
		if value is None and exclude_none:
			continue

		# Relations (add `id`)
		if field.is_relation:
			data[f"{key}_id"] = value
			# Get Display
			if include_display:
				data[f"_{key}_id"] = getattr(instance, field.name).__str__()
		else:
			data[key] = value

		# Display Values
		if len(field.choices or []) > 0 and include_display:
			# Get Display
			data[f"_{key}"] = getattr(instance, f"get_{field.name}_display")()

		# Update Display for Datetime
		if isinstance(value, datetime) and include_display:
			data[f"_{key}"] = value.strftime('%b %d, %y %I:%M %p')

		# Update Display for Date
		elif isinstance(value, date) and include_display:
			data[f"_{key}"] = value.strftime('%b %d, %y')

	# M2M Relations (convert to list) (add `id`)
	for field in m2m_fields:
		key = field.name
		# Check if in Fields (if valid)
		if fields is not None:
			if key not in fields:
				continue

		# Check for exclude
		if key in exclude:
			continue

		value = field.value_from_object(instance)
		# Exclude None where Requested
		if value is None and exclude_none:
			continue

		data[f"{key}_id"] = [rel.id for rel in value]

	# Add Properties
	if properties is not None:
		for property_key in properties:
			obj = getattr(instance, property_key, None)
			if obj is not None:
				if callable(obj):
					data[property_key] = obj()
				else:
					data[property_key] = obj
	return data


def is_empty_value(obj, key):
	val = obj.get(key, None)
	return val is None or val == ""


def model_dict_delta(initial: Dict,
                     current: Dict,
                     include_remove: bool = True,
                     current_fields_only: bool = False) -> Dict:
	if current_fields_only:
		attributes = set(current.keys())
	else:
		attributes = set(initial.keys()).union(current.keys())

	delta = {}
	for key in attributes:
		# Continue of Display Attributes
		if key.startswith('_'):
			continue
		
		# No Initial Value and Current Value (Added)
		if is_empty_value(initial, key) and not is_empty_value(current, key):
			# Add Display
			display_value = current.get(f"_{key}")
			if display_value is not None:
				delta.update({
					key: {
						"type": "added",  "value": current.get(key),
						"display": display_value
					}
				})
			else:
				delta.update({
					key: {"type": "added", "value": current.get(key)}
				})

		# Initial Value and No Current Value (Remove)
		elif not is_empty_value(initial, key) and is_empty_value(current, key) and include_remove:
			delta.update({
				key: {"type": "removed", "value": initial.get(key)}
			})

			# Add Display
			display_value = initial.get(f"_{key}")
			if display_value is not None:
				delta.update({
					key: {
						"type": "removed",  "value": initial.get(key),
						"display": display_value
					}
				})
			else:
				delta.update({
					key: {"type": "removed", "value": initial.get(key)}
				})

		elif not is_empty_value(initial, key) and not is_empty_value(current, key):
			# Initial Value and Current Value are not Equal (Update)

			initial_val = initial.get(key)
			current_val = current.get(key)
			if initial_val != current.get(key):
				# Ensure List Validation is Correct
				if isinstance(initial_val, list) and isinstance(current_val, list):
					try:
						if set(initial_val) == set(current_val):
							# List out of Order pass
							continue
					except TypeError:
						# Unable to compare array of dictionaries
						delta.update({
							key: {
								"type": "updated", "value": current_val,
								"initial": initial_val,
								"display_value": str(current.get(f"_{key}")),
								"display_initial": str(initial.get(f"_{key}"))
							}
						})

				# Add Display
				display_value = initial.get(f"_{key}")
				if display_value is not None:
					delta.update({
						key: {
							"type": "updated", "value": current_val,
							"initial": initial_val,
							"display_value": current.get(f"_{key}"),
							"display_initial": initial.get(f"_{key}")
						}
					})
				else:
					delta.update({
						key: {
							"type": "updated", "value": current_val, "initial": initial_val
						}
					})
	return delta


def not_null_value(val: Any) -> bool:
	if isinstance(val, bool):
		return True

	if isinstance(val, dict) or isinstance(val, list):
		return True

	# Numeric Values
	if isinstance(val, (int, float, complex)) and not isinstance(val, bool):
		if notna(val):
			return True

	if notna(val) and (val or "") not in ("", "nan"):
		return True

	return False


def not_null_record(record: Dict, defaults: Dict = {}) -> Dict:
	clean_record = {
		key: value for key, value in record.items() if not_null_value(val=value)
	}
	clean_record.update({
		key: value for key, value in defaults.items() if key not in clean_record
	})

	return clean_record
