from pathlib import Path
from datetime import datetime

import cv2


class SnapshotService:

    def __init__(self):
        self.snapshot_dir = Path("snapshots")
        self.snapshot_dir.mkdir(exist_ok=True)

    def save(self, frame, person):

        filename = (
            f"tracker_{person.tracker_id}_"
            f"{datetime.now():%Y%m%d_%H%M%S_%f}.jpg"
        )

        filepath = self.snapshot_dir / filename

        success = cv2.imwrite(
            str(filepath),
            frame
        )

        if not success:
            return None

        return str(filepath)