
class Box:
    def __init__(self, canvas, x, y, config):
        self.width = config["box"]["width"]
        self.height = config["box"]["height"]
        self.corners = [x, y, x + self.width, y + self.height]
        self.canvas = canvas
        self.box = canvas.create_rectangle(
            self.corners[0],
            self.corners[1],
            self.corners[2],
            self.corners[3],
            fill=config["box"]["color"]
        )
        self.speed = config["box"]["speed"]
        self.prev_direction = None

    def move(self, direction):
        self.prev_direction = direction
        if direction == "right":
            self.corners[0] += self.speed
            self.corners[2] += self.speed
        elif direction == "left":
            self.corners[0] -= self.speed
            self.corners[2] -= self.speed
        elif direction == "up":
            self.corners[1] -= self.speed
            self.corners[3] -= self.speed
        elif direction == "down":
            self.corners[1] += self.speed
            self.corners[3] += self.speed
    
    def update(self):
        self.canvas.coords(
            self.box,
            self.corners[0],
            self.corners[1],
            self.corners[2],
            self.corners[3]
        )

    def change_color(self, color):
        self.canvas.itemconfig(self.box, fill=color)
