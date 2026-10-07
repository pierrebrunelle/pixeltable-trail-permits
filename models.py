"""Trails (string PK), permits and trailhead check-ins."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import checkin_status, permit_band

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
