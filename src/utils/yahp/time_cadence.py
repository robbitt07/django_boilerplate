
DailyCandence = 'daily'
WeeklyCandence = 'weekly'
MonthlyCadence = 'monthly'
QuarterlyCadence = 'quarterly'
AnnualCadence = 'annual'

CADENCE_CONVERSION_TO_WEEKLY_ROUTER = {
    DailyCandence : lambda x : 7 * x,
    WeeklyCandence : lambda x : x,
    MonthlyCadence : lambda x : x * 12 / 52,
    QuarterlyCadence : lambda x : x * 4 / 52,
    AnnualCadence : lambda x : x / 52,
}

CADENCE_CONVERSION_FROM_WEEKLY_ROUTER = {
    DailyCandence : lambda x : x / 7,
    WeeklyCandence : lambda x : x,
    MonthlyCadence : lambda x : x * 52 / 12,
    QuarterlyCadence : lambda x : x * 52 / 4,
    AnnualCadence : lambda x : x * 52,
}

def convert_cadence_to_weekly(x,cadence):
    try:
        # Round to 6 decimal places here since this is used to write to the database
        return round(CADENCE_CONVERSION_TO_WEEKLY_ROUTER[cadence](float(x)),6)
    except:
        return None

def convert_cadence_from_weekly(x,cadence):
    try:
        # Round to 2 decimal places here since this is used to display to the user
        # This difference in rounding will help to ensure that rounding errors aren't presented to the user
        return round(CADENCE_CONVERSION_FROM_WEEKLY_ROUTER[cadence](float(x)),3)
    except:
        return None

