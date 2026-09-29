from pathlib import Path

from ultralytics import YOLO

from models.person_detection import PersonDetection


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "weights" / "best_v5_only.pt"

CONFIDENCE = 0.1
IOU_THRESHOLD = 0.4
DUPLICATE_IOU = 0.7
CONTAINMENT_THRESHOLD = 0.8
IMAGE_SIZE = 960


class YOLODetector:

    def __init__(self):
        self.model = YOLO(str(MODEL_PATH))

    def detect(self, frame):

        results = self.model.predict(
            source=frame,
            classes=[0],
            conf=CONFIDENCE,
            iou=IOU_THRESHOLD,
            imgsz=IMAGE_SIZE,
            verbose=False
        )

        result = results[0]

        persons = []

        if result.boxes is None:
            return persons

        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()

        for box, confidence in zip(boxes, confidences):

            x1, y1, x2, y2 = map(int, box)

            persons.append(
                PersonDetection(
                    tracker_id=None,
                    confidence=float(confidence),
                    x=x1,
                    y=y1,
                    width=x2 - x1,
                    height=y2 - y1
                )
            )

        persons = self._remove_duplicates(persons)

        return persons

    def _remove_duplicates(self, persons):

        if len(persons) <= 1:
            return persons

        persons = sorted(
            persons,
            key=lambda person: person.confidence,
            reverse=True
        )

        filtered = []

        for person in persons:

            duplicate = False

            box1 = self._get_box(person)

            for existing in filtered:

                box2 = self._get_box(existing)

                iou = self._calculate_iou(
                    box1,
                    box2
                )

                containment = self._calculate_containment(
                    box1,
                    box2
                )

                if (
                    iou >= DUPLICATE_IOU
                    or containment >= CONTAINMENT_THRESHOLD
                ):
                    duplicate = True
                    break

            if not duplicate:
                filtered.append(person)

        return filtered

    def _get_box(self, person):

        return (
            person.x,
            person.y,
            person.x + person.width,
            person.y + person.height
        )

    def _calculate_iou(self, box1, box2):

        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection_width = max(
            0,
            x2 - x1
        )

        intersection_height = max(
            0,
            y2 - y1
        )

        intersection = (
            intersection_width *
            intersection_height
        )

        area1 = (
            (box1[2] - box1[0]) *
            (box1[3] - box1[1])
        )

        area2 = (
            (box2[2] - box2[0]) *
            (box2[3] - box2[1])
        )

        union = area1 + area2 - intersection

        if union <= 0:
            return 0.0

        return intersection / union

    def _calculate_containment(self, box1, box2):

        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection_width = max(
            0,
            x2 - x1
        )

        intersection_height = max(
            0,
            y2 - y1
        )

        intersection = (
            intersection_width *
            intersection_height
        )

        area1 = (
            (box1[2] - box1[0]) *
            (box1[3] - box1[1])
        )

        area2 = (
            (box2[2] - box2[0]) *
            (box2[3] - box2[1])
        )

        smaller_area = min(
            area1,
            area2
        )

        if smaller_area <= 0:
            return 0.0

        return intersection / smaller_area