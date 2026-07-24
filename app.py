import os
import cv2
from dotenv import load_dotenv
from inference import InferencePipeline

from detector.parser import parse_predictions
from services.event_service import EventService
from zone.zone_manager import ZoneManager

load_dotenv()
zone = ZoneManager()
event_service = EventService()

def my_sink(result, video_frame):
    frame = video_frame.image
    people = parse_predictions(result)

    for person in people:
        inside = zone.contains(
            *person.foot_point
        )

        event = event_service.update(
            person,
            inside,
            frame
        )

        if event:
            print(event)

    output_image = result.get("output_image")

    if output_image is not None:
        frame = output_image.numpy_image
        occupied = False

        for person in people:
            if zone.contains(*person.foot_point):
                occupied = True
                break

        zone.draw(
            frame,
            occupied
        )

        if occupied:
            status = "INTRUSION DETECTED"
            color = (0, 0, 255)

        else:
            status = "SAFE"
            color = (0, 255, 0)


        cv2.putText(
            frame,
            status,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            color,
            3

        )

        cv2.imshow(
            "Smart Surveillance",
            frame
        )


        if cv2.waitKey(1) & 0xFF == ord("q"):
            raise KeyboardInterrupt



API_KEY = os.getenv("ROBOFLOW_API_KEY")
WORKSPACE_NAME = os.getenv("WORKSPACE_NAME")
WORKFLOW_ID = os.getenv("WORKFLOW_ID")
VIDEO_REFERENCE = os.getenv("VIDEO_REFERENCE")

pipeline = InferencePipeline.init_with_workflow(
    api_key=API_KEY,
    workspace_name=WORKSPACE_NAME,
    workflow_id=WORKFLOW_ID,
    video_reference=VIDEO_REFERENCE,
    max_fps=30,
    on_prediction=my_sink,
)

pipeline.start()
pipeline.join()