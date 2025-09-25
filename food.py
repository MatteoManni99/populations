import random
from box import Box

class Food(Box):
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
    
    @staticmethod
    def random_position(config):
        x = random.randint(0, config["width"] - config["food"]["width"])
        y = random.randint(0, config["height"] - config["food"]["height"])
        return x, y
    
    @staticmethod
    def spawn_food_event(canvas, config):
        x, y = Food.random_position(config)
        return Food(canvas, x, y, config, config["food"])
      