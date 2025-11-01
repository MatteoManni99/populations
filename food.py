import random
from box import Box

class Food(Box):
    def __init__(self, canvas, x, y, config, config_item):
        self.width = config_item["width"]
        self.height = config_item["height"]
        self.coord = [x, y, x + self.width, y + self.height]
        self.canvas = canvas
        self.center = ((self.coord[0] + self.coord[2]) / 2, (self.coord[1] + self.coord[3]) / 2)
        self.box = canvas.create_rectangle(
            self.coord[0],
            self.coord[1],
            self.coord[2],
            self.coord[3],
            fill=config_item["color"]
        )
        self.corners = [
            (self.coord[0], self.coord[1]),  # top-left
            (self.coord[2], self.coord[1]),  # top-right
            (self.coord[0], self.coord[3]),  # bottom-left
            (self.coord[2], self.coord[3])   # bottom-right
        ]
    
    @staticmethod
    def random_position(config):
        x = random.randint(0, config["world_width"] - config["food"]["width"])
        y = random.randint(0, config["world_height"] - config["food"]["height"])
        return x, y
    
    @staticmethod
    def spawn_food_event(canvas, config):
        x, y = Food.random_position(config)
        return Food(canvas, x, y, config, config["food"])
      