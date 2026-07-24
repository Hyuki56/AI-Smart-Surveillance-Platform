class Event:

    def __init__(
        self,
        event_type,
        person,
        enter_time=None,
        exit_time=None,
        duration=None,
        image_path=None
    ):
        self.event_type = event_type
        self.person = person
        self.enter_time = enter_time
        self.exit_time = exit_time
        self.duration = duration
        self.image_path = image_path

    def __str__(self):
        return (
            f"{self.event_type} | "
            f"Tracker={self.person.tracker_id} | "
            f"Duration={self.duration}"
        )