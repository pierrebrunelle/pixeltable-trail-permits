"""Pixeltable UDFs for trail permits (recorded by module path, e.g. `udfs.permit_band`)."""
import pixeltable as pxt


@pxt.udf
def permit_band(days: int, party_size: int) -> str:
    """Quota band: big or long trips need a ranger review."""
    if party_size > 8 or days > 7:
        return 'review'
    return 'overnight' if days > 1 else 'day-use'


@pxt.udf
def checkin_status(status: str, late_min: int) -> str:
    if status == 'out' and late_min > 120:
        return 'overdue: notify ranger'
    if late_min > 0:
        return f'{status} ({late_min} min late)'
    return status
