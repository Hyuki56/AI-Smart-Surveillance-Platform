import cv2

from detector.yolo_detector import YOLODetector
from tracker.object_tracker import ObjectTracker
from zone.zone_manager import ZoneManager
from services.event_service import EventService


class SurveillanceService:

    def __init__(self, video_path):
        self.video_path = video_path

        self.detector = YOLODetector()
        self.tracker = ObjectTracker()
        self.zone_manager = ZoneManager()
        self.event_service = EventService()

        self.is_running = False

    def run(self):

        if self.is_running:
            return

        self.is_running = True

        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            print("영상을 열 수 없습니다.")
            self.is_running = False
            return

        print("영상 재생 시작")
        print("Q : 종료")

        while self.is_running:

            ret, frame = cap.read()

            if not ret:
                print("영상이 종료되었습니다.")
                break

            # --------------------------------------------------
            # 1. 사람 탐지
            # --------------------------------------------------

            detections = self.detector.detect(frame)

            # --------------------------------------------------
            # 2. 객체 추적
            # --------------------------------------------------

            tracked_persons = self.tracker.update(
                detections
            )

            # --------------------------------------------------
            # 3. 제한구역 내부 사람 확인
            # --------------------------------------------------

            inside_persons = []

            person_inside_states = {}

            for person in tracked_persons:

                foot_x = int(person.foot_point[0])
                foot_y = int(person.foot_point[1])

                inside = self.zone_manager.contains(
                    foot_x,
                    foot_y
                )

                person_inside_states[
                    person.tracker_id
                ] = inside

                if inside:
                    inside_persons.append(person)

            # --------------------------------------------------
            # 4. 제한구역 그리기
            # --------------------------------------------------

            intrusion = len(inside_persons) > 0

            self.zone_manager.draw(
                frame,
                occupied=intrusion
            )

            # --------------------------------------------------
            # 5. 상태 표시
            # --------------------------------------------------

            if intrusion:

                status = "INTRUSION DETECTED"
                status_color = (0, 0, 255)

            else:

                status = "SAFE"
                status_color = (0, 255, 0)

            cv2.putText(
                frame,
                status,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                status_color,
                3
            )

            # --------------------------------------------------
            # 6. Detection / Tracking 정보
            # --------------------------------------------------

            cv2.putText(
                frame,
                f"Detection: {len(detections)}",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Tracking: {len(tracked_persons)}",
                (30, 125),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            # --------------------------------------------------
            # 7. 사람 bbox / ID / 발 위치 표시
            # --------------------------------------------------

            for person in tracked_persons:

                x1 = person.x
                y1 = person.y

                x2 = person.x + person.width
                y2 = person.y + person.height

                foot_x = int(person.foot_point[0])
                foot_y = int(person.foot_point[1])

                inside = person_inside_states.get(
                    person.tracker_id,
                    False
                )

                if inside:

                    color = (0, 0, 255)

                else:

                    color = (0, 255, 0)

                # Bounding Box
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    color,
                    2
                )

                # Tracker ID
                cv2.putText(
                    frame,
                    f"ID: {person.tracker_id}",
                    (
                        x1,
                        max(y1 - 10, 20)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )

                # Foot Point
                cv2.circle(
                    frame,
                    (foot_x, foot_y),
                    5,
                    color,
                    -1
                )

            # --------------------------------------------------
            # 8. 이벤트 처리
            #
            # 이 시점에서는 bbox / ID / Zone / 상태가
            # 이미 frame에 그려져 있다.
            #
            # 따라서 EventService가 ENTER 순간 snapshot을
            # 저장하면 annotated frame이 저장된다.
            # --------------------------------------------------

            events = []

            for person in tracked_persons:

                inside = person_inside_states.get(
                    person.tracker_id,
                    False
                )

                event = self.event_service.update(
                    person,
                    inside,
                    frame
                )

                if event is not None:
                    events.append(event)

            # --------------------------------------------------
            # 9. ENTER / EXIT 이벤트 표시
            #
            # 이벤트 텍스트는 snapshot 저장 이후에 표시된다.
            # --------------------------------------------------

            for event in events:

                person = event.person

                x1 = person.x
                y1 = person.y

                x2 = person.x + person.width
                y2 = person.y + person.height

                if event.event_type == "ENTER":

                    color = (0, 0, 255)

                else:

                    color = (0, 255, 0)

                cv2.putText(
                    frame,
                    event.event_type,
                    (
                        x1,
                        min(
                            y2 + 25,
                            frame.shape[0] - 10
                        )
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )

            # --------------------------------------------------
            # 10. 화면 출력
            # --------------------------------------------------

            cv2.imshow(
                "AI Smart Surveillance Platform",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                self.is_running = False

        cap.release()

        cv2.destroyAllWindows()

        self.is_running = False

        print("프로그램 종료")

    def stop(self):

        self.is_running = False