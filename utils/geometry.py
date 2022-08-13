import numpy as np

EARTH_RADIUS_MILES = 3958.756


def lat_lng_dist(lat_lng_1: tuple, lat_lng_2: tuple) -> float:
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
			Distance as the crow flies from origin lat/lng to destination lat/lng assuming the earth is a sphere or radius EARTH_RADIUS_MILES miles.
	"""
	lat1_rad = float(lat_lng_1[0]) * np.pi / 180
	lng1_rad = float(lat_lng_1[1]) * np.pi / 180
	lat2_rad = float(lat_lng_2[0]) * np.pi / 180
	lng2_rad = float(lat_lng_2[1]) * np.pi / 180
	dlat = lat2_rad - lat1_rad
	dlng = lng2_rad - lng1_rad
	a = np.sin(dlat/2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlng/2) ** 2
	return 2 * EARTH_RADIUS_MILES * np.arctan(a ** .5 / (1-a) ** .5)