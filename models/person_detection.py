class PersonDetection:

    def __init__(self, tracker_id, confidence, x, y, width, height):
        self.tracker_id = tracker_id
        self.confidence = confidence
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def foot_point(self):
        """
        사람의 발 위치 (Zone 판별용)
        """
        return (
            self.x,
            self.y + self.height / 2
        )

    @property
    def bbox(self):
        """
        OpenCV에서 사용할 Bounding Box 좌표
        (x1, y1, x2, y2)
        """
        x1 = self.x - self.width / 2
        y1 = self.y - self.height / 2
        x2 = self.x + self.width / 2
        y2 = self.y + self.height / 2

        return (
            int(x1),
            int(y1),
            int(x2),
            int(y2)
        )