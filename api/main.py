import os
import threading

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.surveillance_service import SurveillanceService


app = FastAPI(
    title="AI Smart Surveillance Platform",
    description="YOLO11 기반 제한구역 침입 탐지 서비스",
    version="1.0.0"
)


VIDEO_PATH = "videos/office.mp4"
SNAPSHOT_DIR = "snapshots"

surveillance_service = SurveillanceService(VIDEO_PATH)
surveillance_thread = None


# --------------------------------------------------
# Response Models
# --------------------------------------------------

class HealthResponse(BaseModel):
    status: str


class StatusResponse(BaseModel):
    is_running: bool


class ControlResponse(BaseModel):
    status: str


class EventResponse(BaseModel):
    event_id: int
    tracker_id: int
    enter_time: str
    exit_time: str | None
    duration: float | None
    image_url: str | None


class EventsResponse(BaseModel):
    events: list[EventResponse]


# --------------------------------------------------
# Health
# --------------------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse
)
def health():

    return {
        "status": "ok"
    }


# --------------------------------------------------
# Status
# --------------------------------------------------

@app.get(
    "/status",
    response_model=StatusResponse
)
def get_status():

    return {
        "is_running": surveillance_service.is_running
    }


# --------------------------------------------------
# Start
# --------------------------------------------------

@app.post(
    "/start",
    response_model=ControlResponse
)
def start_surveillance():

    global surveillance_thread

    if surveillance_service.is_running:

        return {
            "status": "already_running"
        }

    surveillance_thread = threading.Thread(
        target=surveillance_service.run,
        daemon=True
    )

    surveillance_thread.start()

    return {
        "status": "started"
    }


# --------------------------------------------------
# Stop
# --------------------------------------------------

@app.post(
    "/stop",
    response_model=ControlResponse
)
def stop_surveillance():

    if not surveillance_service.is_running:

        return {
            "status": "not_running"
        }

    surveillance_service.stop()

    return {
        "status": "stopped"
    }


# --------------------------------------------------
# Events
# --------------------------------------------------

@app.get(
    "/events",
    response_model=EventsResponse
)
def get_events(
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    )
):

    rows = surveillance_service.event_service.get_recent_events(
        limit=limit
    )

    events = []

    for row in rows:

        image_url = None

        if row[5]:

            filename = os.path.basename(row[5])

            image_url = f"/snapshots/{filename}"

        events.append(
            EventResponse(
                event_id=row[0],
                tracker_id=row[1],
                enter_time=row[2],
                exit_time=row[3],
                duration=row[4],
                image_url=image_url
            )
        )

    return {
        "events": events
    }

# --------------------------------------------------
# Snapshot
# --------------------------------------------------

@app.get(
    "/snapshots/{filename}"
)
def get_snapshot(filename: str):

    file_path = os.path.join(
        SNAPSHOT_DIR,
        filename
    )

    if not os.path.isfile(file_path):

        raise HTTPException(
            status_code=404,
            detail="Snapshot not found"
        )

    return FileResponse(
        file_path,
        media_type="image/jpeg"
    )