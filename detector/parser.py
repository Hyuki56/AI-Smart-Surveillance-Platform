from models.person_detection import PersonDetection


def parse_predictions(result):
    """
    Roboflow Workflow 결과를 PersonDetection 객체 리스트로 변환한다.
    """

    detections = result.get("predictions")

    if detections is None:
        return []

    people = []

    # 탐지된 사람이 없는 경우
    if len(detections.xyxy) == 0:
        return people

    for i in range(len(detections.xyxy)):

        # Bounding Box
        x1, y1, x2, y2 = detections.xyxy[i]

        width = x2 - x1
        height = y2 - y1

        center_x = x1 + width / 2
        center_y = y1 + height / 2

        # Confidence
        confidence = float(detections.confidence[i])

        # Tracker ID
        tracker_id = None
        if detections.tracker_id is not None:
            tracker_id = int(detections.tracker_id[i])

        person = PersonDetection(
            tracker_id=tracker_id,
            confidence=confidence,
            x=float(center_x),
            y=float(center_y),
            width=float(width),
            height=float(height),
        )

        people.append(person)

    return people