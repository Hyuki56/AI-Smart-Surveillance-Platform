import cv2
import numpy as np

class ZoneManager:
    def __init__(self):
        self.points = np.array(
            [
                (650,700),
                (1000,700),
                (1100,250),
                (950,250)
            ],
            dtype=np.int32
        )

    def contains(self, x, y):
        point = np.array(
            [
                [x, y]
            ],
            dtype=np.float32
        )

        result = cv2.pointPolygonTest(
            self.points,
            (x, y),
            False
        )

        return result >= 0


    def draw(self, frame, occupied=False):
        color = (
            (0,0,255)
            if occupied
            else
            (0,255,0)
        )

        cv2.polylines(
            frame,
            [
                self.points
            ],
            True,
            color,
            3
        )

        text = "RESTRICTED ZONE"

        cv2.putText(
            frame,
            text,
            (
                self.points[0][0],
                self.points[0][1] - 10
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )