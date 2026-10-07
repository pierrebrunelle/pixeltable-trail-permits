"""Trail Permit API built with Pixeltable.

    pxt schema update app.py trails
    pxt service run app.py trails
"""
from pixeltable.serving import FastAPIRouter

from models import Checkins, Permits, TableModel, Trails  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import open_trails, permits_for

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
