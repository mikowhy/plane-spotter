from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from planespotter import matcher
from planespotter.camera import Camera
from planespotter.database import get_history
from planespotter.flights import FlightTracker
from planespotter.matcher import find_approaching, get_nearby

app = FastAPI(title="Plane Spotter")

templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(templates_dir))
if static_dir.exists():
    app.mount(
        path="/static",
        app=StaticFiles(directory=str(static_dir)),
        name="static",
    )

favicon_path = static_dir / "favicon.svg"


@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    return FileResponse(
        path=str(favicon_path),
        media_type="image/svg+xml",
    )


camera: Camera | None = None
tracker: FlightTracker | None = None


def setup(
    camera_instance: Camera | None,
    tracker_instance: FlightTracker | None,
) -> None:
    global camera, tracker
    camera = camera_instance
    tracker = tracker_instance


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
    )


@app.get("/stream")
async def stream() -> StreamingResponse:
    if camera is None:
        return StreamingResponse(
            content=iter([]),
            status_code=503,
        )
    return StreamingResponse(
        content=camera.stream_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/flights")
async def flights() -> dict:
    if tracker is None:
        return {"aircraft": [], "approaching": [], "nearby": []}

    all_aircraft = tracker.aircraft
    approaching = find_approaching(all_aircraft)
    nearby = get_nearby(all_aircraft)

    return {
        "aircraft": [plane.to_dict() for plane in all_aircraft],
        "approaching": [plane.to_dict() for plane in approaching],
        "nearby": [plane.to_dict() for plane in nearby],
    }


@app.get("/location")
async def location() -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Home", "icon": "home"},
                "geometry": {"type": "Point", "coordinates": [matcher.HOME_LON, matcher.HOME_LAT]},
            },
            {
                "type": "Feature",
                "properties": {"name": "Lawica Airport (EPPO)", "icon": "airport"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [matcher.AIRPORT_LON, matcher.AIRPORT_LAT],
                },
            },
        ],
    }


@app.get("/history")
async def history(
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    return await get_history(
        limit=limit,
        offset=offset,
    )
