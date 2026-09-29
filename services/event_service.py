from datetime import datetime

from database.repository import EventRepository
from models.event import Event
from services.snapshot_service import SnapshotService


class EventService:

    def __init__(self):
        self.previous_state = {}
        self.enter_times = {}

        self.snapshot_service = SnapshotService()
        self.repository = EventRepository()

    def update(self, person, inside, frame):

        tracker_id = person.tracker_id

        print(
            "tracker_id:",
            tracker_id,
            "inside:",
            inside
        )

        if tracker_id is None:
            return None

        previous_inside = self.previous_state.get(
            tracker_id,
            False
        )

        # -----------------------------------------
        # ENTER
        # -----------------------------------------

        if not previous_inside and inside:

            enter_time = datetime.now()

            self.previous_state[tracker_id] = True
            self.enter_times[tracker_id] = enter_time

            image_path = self.snapshot_service.save(
                frame,
                person
            )

            self.repository.create_entry(
                tracker_id=tracker_id,
                enter_time=enter_time,
                image_path=image_path
            )

            return Event(
                event_type="ENTER",
                person=person,
                enter_time=enter_time,
                image_path=image_path
            )

        # -----------------------------------------
        # EXIT
        # -----------------------------------------

        if previous_inside and not inside:

            exit_time = datetime.now()

            enter_time = self.enter_times.pop(
                tracker_id,
                exit_time
            )

            duration = (
                exit_time - enter_time
            ).total_seconds()

            self.previous_state[tracker_id] = False

            self.repository.update_exit(
                tracker_id=tracker_id,
                exit_time=exit_time,
                duration=duration
            )

            return Event(
                event_type="EXIT",
                person=person,
                enter_time=enter_time,
                exit_time=exit_time,
                duration=duration
            )

        return None

    # -----------------------------------------
    # Recent Events
    # -----------------------------------------

    def get_recent_events(self, limit=10):

        return self.repository.find_recent_events(
            limit=limit
        )