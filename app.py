"""Trail Permit API built with Pixeltable.

    pxt schema update app.py trails
    pxt service run app.py trails
"""
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

from udfs import checkin_status, permit_band

# ---- tables ----
TableModel = pxt.model_base()


class Trails(TableModel, name='trails'):
    code = pxt.Column(type=pxt.String, primary_key=True)
    name: pxt.String
    region: pxt.String
    miles: pxt.Float
    difficulty: pxt.String
    open: pxt.Bool

    region_upper = pxtf.string.upper(region)
    name_lower = pxtf.string.lower(name)


class Permits(TableModel, name='permits'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    trail_code: pxt.String
    holder: pxt.String
    days: pxt.Int
    party_size: pxt.Int
    start_date: pxt.String
    notes: pxt.String | None

    band = permit_band(days, party_size)
    trail_upper = pxtf.string.upper(trail_code)


class Checkins(TableModel, name='checkins'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    permit_holder: pxt.String
    trail_code: pxt.String
    status: pxt.String          # in / out
    late_min: pxt.Int
    gate: pxt.String
    note: pxt.String | None

    status_label = checkin_status(status, late_min)
    gate_upper = pxtf.string.upper(gate)


# ---- queries ----
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


# ---- routes ----
trails_api = FastAPIRouter(name='trails_api')
trails_api.add_insert_route(Trails, path='/trails',
                            inputs=[Trails.code, Trails.name, Trails.region, Trails.miles, Trails.difficulty, Trails.open],
                            outputs=[Trails.code, Trails.region_upper, Trails.name_lower])
trails_api.add_insert_route(Permits, path='/permits',
                            inputs=[Permits.trail_code, Permits.holder, Permits.days, Permits.party_size,
                                    Permits.start_date, Permits.notes],
                            outputs=[Permits.id, Permits.band, Permits.trail_upper])
trails_api.add_insert_route(Checkins, path='/checkins',
                            inputs=[Checkins.permit_holder, Checkins.trail_code, Checkins.status, Checkins.late_min,
                                    Checkins.gate, Checkins.note],
                            outputs=[Checkins.id, Checkins.status_label, Checkins.gate_upper])
trails_api.add_compute_route(Permits, path='/band', inputs=[Permits.days, Permits.party_size], outputs=[Permits.band])
trails_api.add_query_route(path='/trails/open', query=open_trails, method='get')
trails_api.add_query_route(path='/permits/by-trail', query=permits_for, method='get')
