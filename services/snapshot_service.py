from pathlib import Path
from datetime import datetime

import cv2


class SnapshotService:
    def __init__(self):
        self.snapshot_dir = Path("snapshots")
        self.snapshot_dir.mkdir(exist_ok=True)

    def save(self, frame, person):
        x1, y1, x2, y2 = person.bbox
        frame_height, frame_width = frame.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame_width, x2)
        y2 = min(frame_height, y2)

        crop = frame[y1:y2, x1:x2]

        if crop.size == 0:
            return None

        filename = (
            f"tracker_{person.tracker_id}_"
            f"{datetime.now():%Y%m%d_%H%M%S}.jpg"
        )

        filepath = self.snapshot_dir / filename

        cv2.imwrite(str(filepath), crop)

        return str(filepath)

