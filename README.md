<!-- pixeltable-example-app: 20261002-trail-permits -->
# Trail Permit API built with Pixeltable

[![Built with Pixeltable](https://img.shields.io/badge/built%20with-Pixeltable-5b4bff)](https://pixeltable.com)
[![PyPI - pixeltable](https://img.shields.io/pypi/v/pixeltable?label=pixeltable)](https://pypi.org/project/pixeltable/)
[![GitHub stars](https://img.shields.io/github/stars/pixeltable/pixeltable?style=social)](https://github.com/pixeltable/pixeltable)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

A ranger station's permit desk: **trails** (with a string trail code), **permits** issued to hikers for a number of days and a party size, and **check-ins** at trailhead gates. Pixeltable computes a permit band, normalized labels and a late-arrival status. The example is built around operating the service on **Pixeltable Cloud** with the `pxt` CLI: create the database from `pixeltable.toml`, push the schema, start the service, then check status and logs, stop, start and restart.

[Pixeltable](https://pixeltable.com) is open-source, Python-native **multimodal AI data infrastructure**: tables, incremental computed columns, UDFs, indexes and serving in one library, running locally or on Pixeltable Cloud.

> ⭐ **Like this example?** Star [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable) on GitHub. It helps other developers find it.

## What this example shows

- **Pixeltable Cloud lifecycle** from the `pxt` CLI (`db`, `schema`, `service`)
- **`pixeltable.toml` project config**: local and Pixeltable Cloud database sizing in one file
- **Multi-table layout and schema evolution** with `pxt schema update`
- **Incremental computed columns** powered by plain Python UDFs (`@pxt.udf`)
- **FastAPI serving**: one `FastAPIRouter` turns tables and `@pxt.query` functions into typed REST routes (insert, update, delete, compute and query) with OpenAPI docs
- **Importable UDF module**: UDFs in `udfs.py`, tables in `models.py`, queries in `queries.py`, routes in `app.py` (Pixeltable resolves UDFs by module path)
- **`pixeltable.toml`** declares a local database and a **Pixeltable Cloud** database, so the same code deploys with `pxt db update`

## Operating it on Pixeltable Cloud

```bash
U=pxt://<your-org>:<your-db>
pxt db update $U                     # create or resize the database from pixeltable.toml
pxt db status $U                     # state, cpu/memory, image
pxt schema update app.py $U/trails   # tables
pxt service update app.py $U/trails  # API (rerun after code changes)
pxt service list $U                  # hosted URL and routes
pxt service logs trails_api --tail 50   # recent service logs
pxt db logs $U --tail 50
pxt db stop $U && pxt db start $U    # pause/resume; data is kept
pxt db restart $U                    # e.g. after `pxt secret set`
```

`pixeltable.toml` keeps capacity in version control (`cpu`, `memory_mb`, `disk_gb`, `workers`). Change it and rerun `pxt db update` to apply the new size.

## What's inside

| File | What it is |
|------|------------|
| `app.py` | The API: one `FastAPIRouter` wiring the tables and queries into REST routes |
| `client_demo.py` | Band a trip, issue a permit, check a party in and out, and browse trails through the API |
| `models.py` | Tables declared as Python classes: columns, computed columns, indexes |
| `pixeltable.toml` | Project config: the local database plus a Pixeltable Cloud database (sizing, deploy excludes) |
| `queries.py` | `@pxt.query` functions served as query routes |
| `seed.py` | Seed trails and a few permits |
| `udfs.py` | Pixeltable UDFs (`@pxt.udf`) in their own importable module |
| `requirements.txt` / `pyproject.toml` | Dependencies (`pixeltable[serve]>=0.7.14`) |

**Tables**

| Table | Stored columns | Computed columns |
|-------|---------|------------------|
| `trails` | `code`, `name`, `region`, `miles`, `difficulty`, `open` | `region_upper`, `name_lower` |
| `permits` | `trail_code`, `holder`, `days`, `party_size`, `start_date`, `notes` | `id`, `band`, `trail_upper` |
| `checkins` | `permit_holder`, `trail_code`, `status`, `late_min`, `gate`, `note` | `id`, `status_label`, `gate_upper` |

**API routes** (service `trails_api`)

| Method | Path | Kind | Backed by | Notes |
|--------|------|------|-----------|-------|
| `POST` | `/trails` | insert | `Trails` |  |
| `POST` | `/permits` | insert | `Permits` |  |
| `POST` | `/checkins` | insert | `Checkins` |  |
| `POST` | `/band` | compute | `Permits` |  |
| `GET` | `/trails/open` | query | `open_trails` |  |
| `GET` | `/permits/by-trail` | query | `permits_for` |  |

## Quickstart

Requires Python 3.11+ and `pixeltable[serve]>=0.7.14`.

```bash
git clone https://github.com/pierrebrunelle/pixeltable-trail-permits.git
cd pixeltable-trail-permits
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create the tables in a local catalog directory named `trails`
pxt schema update app.py trails

python seed.py trails
pxt service run app.py trails --port 8000   # open http://localhost:8000/docs
python client_demo.py                      # in another terminal
```

Try it:

```bash
curl -s -X POST localhost:8000/band -H 'Content-Type: application/json' -d '{"days": 2, "party_size": 9}'
curl -s 'localhost:8000/trails/open?region=cascades'
```

## Deploy to Pixeltable Cloud

The same `app.py` runs on [Pixeltable Cloud](https://pixeltable.com). Sign in (or get a free trial database with `pxt new`), point the second database entry in `pixeltable.toml` at your own database, then deploy:

```bash
pxt login                       # or: export PIXELTABLE_API_KEY=<your-api-key>
# edit pixeltable.toml: name = 'pxt://<your-org>:<your-db>'
pxt db update pxt://<your-org>:<your-db>                 # build the image and upload the project
pxt schema update app.py pxt://<your-org>:<your-db>/trails   # create the tables in the hosted database
pxt service update app.py pxt://<your-org>:<your-db>/trails  # start the API there
pxt service list pxt://<your-org>:<your-db>              # list hosted services
```

Hosted routes require an API key: send it in the `X-api-key` header (for example `-H "X-api-key: $PIXELTABLE_API_KEY"`). Keep keys in environment variables or `pxt secret set`, never in code.

## Code walkthrough

**1. Business logic is plain Python, in `udfs.py`.** A `@pxt.udf` function can be used as a column expression. Pixeltable records UDFs by module path (`udfs.permit_band`), so they live in their own importable module rather than inline in the app: the daemon, serving workers and Pixeltable Cloud import it again by that path.

```python
# udfs.py
@pxt.udf
def permit_band(days: int, party_size: int) -> str:
    """Quota band: big or long trips need a ranger review."""
    if party_size > 8 or days > 7:
        return 'review'
    return 'overnight' if days > 1 else 'day-use'
```

**2. Tables are Python classes (`models.py`).** Annotated attributes are stored columns; attributes assigned an expression are **computed columns** (`id`, `band`, `trail_upper`), evaluated incrementally on every insert or update and recomputed when their inputs change.

```python
# models.py
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
```

**3. Queries are functions (`queries.py`).** `@pxt.query` wraps a Pixeltable query so it can be called from Python or exposed as a route:

```python
# queries.py
@pxt.query
def open_trails(region: str):
    return Trails.where((Trails.region == region) & (Trails.open == True)).select(  # noqa: E712
        Trails.code, Trails.name, Trails.miles, Trails.difficulty
    ).order_by(Trails.miles)
```

**4. One router, a full REST API.** `FastAPIRouter` generates request/response models from the column types, validates input, and publishes OpenAPI docs at `/docs`:

```python
# app.py
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
```

## Learn more

- 🌐 Website: https://pixeltable.com
- 📚 Docs: https://docs.pixeltable.com
- 💻 Source: https://github.com/pixeltable/pixeltable (⭐ star it if Pixeltable is useful to you)
- 📦 PyPI: https://pypi.org/project/pixeltable/

---

<sub>Built as part of a daily series of Pixeltable example apps · Pixeltable 0.7.14 · Python, FastAPI, incremental computed columns · Licensed under Apache-2.0.</sub>
