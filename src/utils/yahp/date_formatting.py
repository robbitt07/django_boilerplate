
import pandas as pd 

def get_formatted_date(x):
	try:
		return pd.to_datetime(x).strftime('%Y-%m-%dT%H:%M')
	except:
		return None
