from django.db.models.expressions import RawSQL

import numpy as np
from typing import Tuple


EARTH_RADIUS_MILES = 3958.756


def get_simple_distance_raw_sql(latitude_field: str,
                                longitude_field: str,
                                latitude: float,
                                longitude: float):
	"""
	Return raw sql for Django Model to Query a Field -> Simple Estimate of Distance

	Parameters
	-----------
		latitude_field str
			Django Model Latitude Field
		longitude_field str
			Django Model Longitude Field
		latitude float
			Input Latitude
		longitude float
			Input Longitude

	Example
	-----------
		get_simple_distance_raw_sql(
			latitude_field='commongeo_shape.c_latitude',
			longitude_field='commongeo_shape.c_longitude',
			latitude=abstract_shape.c_latitude,
			longitude=abstract_shape.c_longitude
		)
	"""
	simple_formula = f"({latitude_field} - %s)^2 + ({longitude_field} - %s)^2"
	return RawSQL(simple_formula, (latitude, longitude))


def get_distance_raw_sql(latitude_field: str, longitude_field: str, latitude: float, longitude: float):
	"""
	Return raw sql for Django Model to Query a Field

	Parameters
	-----------
		latitude_field str
			Django Model Latitude Field
		longitude_field str
			Django Model Longitude Field
		latitude float
			Input Latitude
		longitude float
			Input Longitude

	Example
	-----------
		get_distance_raw_sql(
			latitude_field='commongeo_shape.c_latitude',
			longitude_field='commongeo_shape.c_longitude',
			latitude=abstract_shape.c_latitude,
			longitude=abstract_shape.c_longitude
		)
	"""
	# Great circle distance formula
	gcd_formula = f"3958 * acos(least(greatest(\
	cos(radians(%s)) * cos(radians({latitude_field})) \
	* cos(radians({longitude_field}) - radians(%s)) + \
	sin(radians(%s)) * sin(radians({latitude_field})) \
	, -1), 1))"
	return RawSQL(
		gcd_formula,
		(latitude, longitude, latitude)
	)


def lat_lng_dist(lat_lng_1: Tuple[float, float], lat_lng_2: Tuple[float, float]) -> float:
	"""
	Description
	-----------
		Distance as the crow flies, assuming the earther is a sphere.

	Parameters
	-----------
		lat_lng_1: Tuple (float,float)
			(<float: orig_lat>, <float: orig_lng>)
		lat_lng_2: Tuple (float,float)
			(<float: term_lat>, <float: term_lng>)

	Returns
	-----------
		Float
			Distance as the crow flies from origin lat/lng to destination lat/lng 
	        assuming the earth is a sphere or radius EARTH_RADIUS_MILES miles.
	"""
	lat1_rad = float(lat_lng_1[0]) * np.pi / 180
	lng1_rad = float(lat_lng_1[1]) * np.pi / 180
	lat2_rad = float(lat_lng_2[0]) * np.pi / 180
	lng2_rad = float(lat_lng_2[1]) * np.pi / 180
	dlat = lat2_rad - lat1_rad
	dlng = lng2_rad - lng1_rad
	a = (
        np.sin(dlat/2) ** 2 + np.cos(lat1_rad) *
        np.cos(lat2_rad) * np.sin(dlng/2) ** 2
    )
	return 2 * EARTH_RADIUS_MILES * np.arctan(a ** .5 / (1-a) ** .5)
