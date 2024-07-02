
def distance(miles: float) -> str:
	if miles < 0.5:
		return f"{miles*5280:,.0f}ft"

	return f"{miles:,.1f}mi"
