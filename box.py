
class Box:
    def __init__(self, canvas, x, y, config):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.width = config["box"]["width"]
        self.height = config["box"]["height"]
        self.corners = [(x, y), (x + self.width, y), (x + self.width, y + self.height), (x, y + self.height)]

        self.canvas = canvas
        self.box = canvas.create_rectangle(
            x, y,
            x + self.width,
            y + self.height,
            fill=config["box"]["color"]
        )
    
    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.canvas.coords(self.box, self.x, self.y, self.x + self.width, self.y + self.height)
    