from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from planespotter.camera import Camera
from planespotter.database import get_history
from planespotter.flights import FlightTracker
from planespotter.matcher import AIRPORT_LAT, AIRPORT_LON, HOME_LAT, HOME_LON, find_approaching, get_nearby

app = FastAPI(title="Plane Spotter")

templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(templates_dir))
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

camera: Camera | None = None
tracker: FlightTracker | None = None


def setup(cam: Camera, trk: FlightTracker) -> None:
    global camera, tracker
    camera = cam
    tracker = trk


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/stream")
async def stream() -> StreamingResponse:
    if camera is None:
        return StreamingResponse(iter([]), status_code=503)
    return StreamingResponse(
        camera.stream_frames(),
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
        "aircraft": [ac.to_dict() for ac in all_aircraft],
        "approaching": [ac.to_dict() for ac in approaching],
        "nearby": [ac.to_dict() for ac in nearby],
    }


@app.get("/location")
async def location() -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Home", "icon": "home"},
                "geometry": {"type": "Point", "coordinates": [HOME_LON, HOME_LAT]},
            },
            {
                "type": "Feature",
                "properties": {"name": "Lawica Airport (EPPO)", "icon": "airport"},
                "geometry": {
                    "type": "Point",
                    "coordinates": [AIRPORT_LON, AIRPORT_LAT],
                },
            },
        ],
    }


@app.get("/history")
async def history(limit: int = 50, offset: int = 0) -> list[dict]:
    return await get_history(limit=limit, offset=offset)
