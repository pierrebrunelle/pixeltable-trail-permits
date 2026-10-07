"""Trail desk queries."""
import pixeltable as pxt

from models import Permits, Trails


@pxt.query
def open_trails(region: str):
    return Trails.where((Trails.region == region) & (Trails.open == True)).select(  # noqa: E712
        Trails.code, Trails.name, Trails.miles, Trails.difficulty
    ).order_by(Trails.miles)


@pxt.query
def permits_for(trail_code: str):
    return Permits.where(Permits.trail_code == trail_code).select(
        Permits.holder, Permits.start_date, Permits.days, Permits.party_size, Permits.band
    ).order_by(Permits.start_date)
