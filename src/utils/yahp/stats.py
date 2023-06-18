import numpy as np
from typing import Any, List


def nunique(x: Any) -> int:
    return len(np.unique(x))


def get_numeric_stats(measurements : List[float], precision : int=2):
	'''
	Get Standard Descriptive Statistics for a List of Numeric Values

	Parameters
	------------
	measurements : List[float]
		List of numeric values (float/int/etc)
	
	Returns
	------------
	stats : Dict
		Dictionary of descriptive statistics of the measurements provided
	'''
	return {
		'count' : len(measurements),
		'min' : round(min(measurements),precision),
		'max' : round(max(measurements),precision),
		'avg' : round(np.mean(measurements),precision),
		'stdev' : round(np.var(measurements) ** .5,precision),
		'first_quartile' : round(np.percentile(measurements,25),precision),
		'median' : round(np.percentile(measurements,50),precision),
		'third_quartile' : round(np.percentile(measurements,75),precision),
	}
