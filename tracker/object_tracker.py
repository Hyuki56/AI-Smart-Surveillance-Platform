import numpy as np
import supervision as sv

from models.person_detection import PersonDetection


class ObjectTracker:

    def __init__(self):

        self.tracker = sv.ByteTrack(
            track_activation_threshold=0.1,
            lost_track_buffer=120,
            minimum_matching_threshold=1,
            frame_rate=30
        )

        self.frame_count = 0

    def update(self, persons):

        self.frame_count += 1

        print(
            f"\n========== FRAME {self.frame_count} =========="
        )

        print(
            f"YOLO Detection: {len(persons)}"
        )

        if not persons:

            print("ByteTrack Input: EMPTY")

            detections = sv.Detections.empty()

            tracked = self.tracker.update_with_detections(
                detections
            )

            print(
                f"ByteTrack Output: {len(tracked)}"
            )

            return []

        xyxy = []
        confidence = []

        for i, person in enumerate(persons):

            x1 = float(person.x)
            y1 = float(person.y)

            x2 = float(
                person.x + person.width
            )

            y2 = float(
                person.y + person.height
            )

            xyxy.append([
                x1,
                y1,
                x2,
                y2
            ])

            confidence.append(
                float(person.confidence)
            )

            print(
                f"DET {i}: "
                f"bbox=({int(x1)}, {int(y1)}, "
                f"{int(x2)}, {int(y2)}) "
                f"conf={person.confidence:.3f}"
            )

        detections = sv.Detections(
            xyxy=np.array(
                xyxy,
                dtype=np.float32
            ),
            confidence=np.array(
                confidence,
                dtype=np.float32
            ),
            class_id=np.zeros(
                len(persons),
                dtype=int
            )
        )

        print(
            f"ByteTrack Input: {len(detections)}"
        )

        tracked = self.tracker.update_with_detections(
            detections
        )

        print(
            f"ByteTrack Output: {len(tracked)}"
        )

        if len(tracked) > 0:

            print(
                "Track IDs:",
                tracked.tracker_id.tolist()
            )

            for i in range(len(tracked)):

                print(
                    f"  TRACK {i}: "
                    f"ID={tracked.tracker_id[i]} "
                    f"bbox={tracked.xyxy[i].astype(int).tolist()} "
                    f"conf={tracked.confidence[i]:.3f}"
                )

        else:

            print(
                "  NO ACTIVE TRACKS"
            )

        result = []

        for i in range(len(tracked)):

            tracker_id = int(
                tracked.tracker_id[i]
            )

            x1, y1, x2, y2 = tracked.xyxy[i]

            confidence = float(
                tracked.confidence[i]
            )

            result.append(
                PersonDetection(
                    tracker_id=tracker_id,
                    confidence=confidence,
                    x=int(x1),
                    y=int(y1),
                    width=int(x2 - x1),
                    height=int(y2 - y1)
                )
            )

        return result