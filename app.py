from services.surveillance_service import SurveillanceService


VIDEO_PATH = "videos/office.mp4"


def main():

    service = SurveillanceService(
        VIDEO_PATH
    )

    service.run()


if __name__ == "__main__":
    main()