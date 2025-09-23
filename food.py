import random

class Food:
    def __init__(self, canvas, x, y, config, config_item):
        self.width = config_item["width"]
        self.height = config_item["height"]
        self.corners = [x, y, x + self.width, y + self.height]
        self.canvas = canvas
        self.box = canvas.create_rectangle(
            self.corners[0],
            self.corners[1],
            self.corners[2],
            self.corners[3],
            fill=config_item["color"]
        )

        self.prev_direction = None

    def update(self):
        self.canvas.coords(
            self.box,
            self.corners[0],
            self.corners[1],
            self.corners[2],
            self.corners[3]
        )