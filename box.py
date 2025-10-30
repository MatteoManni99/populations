import random

class Box:
    def __init__(self, canvas, x, y, config, config_box):
        self.width = config_box["width"]
        self.height = config_box["height"]
        self.growth_width_limit = config_box["growth_width_limit"]
        self.growth_height_limit = config_box["growth_height_limit"]
        
        self.corners = [x, y, x + self.width, y + self.height]
        self.canvas = canvas
        self.box = canvas.create_rectangle(
            self.corners[0],
            self.corners[1],
            self.corners[2],
            self.corners[3],
            fill=config_box["color"]
        )
        self.speed = config_box["speed"]
        self.possible_directions = config["possible_directions"]
        self.score = 0
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
    
    def box_update(self):
        self.canvas.coords(
            self.box,
            self.corners[0],
            self.corners[1],
            self.corners[2],
            self.corners[3]
        )

    def change_color(self, color):
        self.canvas.itemconfig(self.box, fill=color)
    
    @staticmethod
    def choose_direction(box, inertia_probability = 0.95):
        if box.prev_direction is None:
            return random.choice(box.possible_directions)
        elif random.random() > inertia_probability:
            return random.choice(box.possible_directions)
        else:
            return box.prev_direction
    
    @staticmethod
    def check_box_collision(box1, box2, direction):
        if direction == "up":
            return ((box2.corners[0] < box1.corners[0] and box1.corners[0] < box2.corners[2]) or \
                    (box2.corners[0] < box1.corners[2] and box1.corners[2] < box2.corners[2]) or\
                    (box2.corners[0] == box1.corners[0] and box1.corners[2] == box2.corners[2]) or\
                    (box1.corners[0] <= box2.corners[0] and box1.corners[2] >= box2.corners[2])) and \
                    box1.corners[1] - box1.speed < box2.corners[3] and \
                    box1.corners[3] > box2.corners[1]
                    
        elif direction == "down":
            return ((box2.corners[0] < box1.corners[0] and box1.corners[0] < box2.corners[2]) or \
                    (box2.corners[0] < box1.corners[2] and box1.corners[2] < box2.corners[2]) or \
                    (box2.corners[0] == box1.corners[0] and box1.corners[2] == box2.corners[2])or \
                    (box1.corners[0] <= box2.corners[0] and box1.corners[2] >= box2.corners[2])) and \
                    box1.corners[3] + box1.speed > box2.corners[1] and \
                    box1.corners[1] < box2.corners[3]
        
        elif direction == "left":
            return ((box2.corners[1] < box1.corners[1] and box1.corners[1] < box2.corners[3]) or \
                    (box2.corners[1] < box1.corners[3] and box1.corners[3] < box2.corners[3]) or \
                    (box2.corners[1] == box1.corners[1] and box1.corners[3] == box2.corners[3]) or \
                    (box1.corners[1] <= box2.corners[1] and box1.corners[3] >= box2.corners[3])) and \
                    box1.corners[0] - box1.speed < box2.corners[2] and \
                    box1.corners[2] > box2.corners[0]
        
        elif direction == "right":
            return ((box2.corners[1] < box1.corners[1] and box1.corners[1] < box2.corners[3]) or \
                    (box2.corners[1] < box1.corners[3] and box1.corners[3] < box2.corners[3]) or \
                    (box2.corners[1] == box1.corners[1] and box1.corners[3] == box2.corners[3]) or \
                    (box1.corners[1] <= box2.corners[1] and box1.corners[3] >= box2.corners[3])) and \
                    box1.corners[2] + box1.speed > box2.corners[0] and \
                    box1.corners[0] < box2.corners[2]
        
        else: return False
    
    @staticmethod
    def check_border_collision(box, direction, width, height):
        if direction == "up":
            return box.corners[1] - box.speed < 0
        elif direction == "down":
            return box.corners[3] + box.speed > height
        elif direction == "left":
            return box.corners[0] - box.speed < 0
        elif direction == "right":
            return box.corners[2] + box.speed > width
    
    def eat_food(self):
        self.change_dimensions(self.width + 2, self.height + 2)
        self.score += 1
    
    def change_dimensions(self, new_width, new_height):
        # TODO: Center the box when changing dimensions
        if new_width <= self.growth_width_limit:
            self.width = new_width
            self.corners[2] = self.corners[0] + self.width
        if new_height <= self.growth_height_limit:
            self.height = new_height
            self.corners[3] = self.corners[1] + self.height
        self.box_update()
        