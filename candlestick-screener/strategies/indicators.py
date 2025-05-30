import json

def pivot_levels(high: float, low: float, close: float) -> dict:
    """
    Calculate pivot levels including Pivot, R1-R4, S1-S4, Bottom CPR, Top CPR.

    Args:
        high (float): Daily high price
        low (float): Daily low price
        close (float): Daily close price

    Returns:
        dict: A dictionary containing all pivot levels
    """
    pivot = (high + low + close) / 3
    bc = (high + low) / 2
    tc = (pivot - bc) + pivot

    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    s3 = pivot - 2 * (high - low)
    s4 = pivot - 3 * (high - low)

    r1 = (2 * pivot) - low
    r2 = pivot + (high - low)
    r3 = pivot + 2 * (high - low)
    r4 = pivot + 3 * (high - low)

    pivot_data = {
        'pivot': round(pivot, 4),
        'bottomCpr': round(bc, 4),
        'topCpr': round(tc, 4),
        's1': round(s1, 4),
        's2': round(s2, 4),
        's3': round(s3, 4),
        's4': round(s4, 4),
        'r1': round(r1, 4),
        'r2': round(r2, 4),
        'r3': round(r3, 4),
        'r4': round(r4, 4),
    }
    
    return json.dumps(pivot_data)