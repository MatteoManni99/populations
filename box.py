import random

class Box:
    def __init__(self, canvas, x, y, config, config_box):
        self.width = config_box["width"]
        self.height = config_box["height"]
        self.growth_width_limit = config_box["growth_width_limit"]
        self.growth_height_limit = config_box["growth_height_limit"]
        self.vision_range = config_box["vision_range"]
        self.canvas = canvas
        self.default_color = config_box["color"]
        self.coord = [x, y, x + self.width, y + self.height]
        self.center = ((self.coord[0] + self.coord[2]) / 2, (self.coord[1] + self.coord[3]) / 2)
        self.box = canvas.create_rectangle(
            self.coord[0],
            self.coord[1],
            self.coord[2],
            self.coord[3],
            fill=self.default_color
        )
        if (config["plot_vision_range"]):
            self.vision_circle = canvas.create_oval(
                self.center[0] - self.vision_range,
                self.center[1] - self.vision_range,
                self.center[0] + self.vision_range,
                self.center[1] + self.vision_range,
                outline="lightgrey"
            )
        else:
            self.vision_circle = None
        self.corners = [
            (self.coord[0], self.coord[1]),  # top-left
            (self.coord[2], self.coord[1]),  # top-right
            (self.coord[0], self.coord[3]),  # bottom-left
            (self.coord[2], self.coord[3])   # bottom-right
        ]

        self.manual_control = False
        self.speed = config_box["speed"]
        self.possible_directions = config["possible_directions"]
        self.prev_direction = random.choice(self.possible_directions)
        self.score = 0

    def move(self, direction):
        self.prev_direction = direction
        if direction == "right":
            self.coord[0] += self.speed
            self.coord[2] += self.speed
        elif direction == "left":
            self.coord[0] -= self.speed
            self.coord[2] -= self.speed
        elif direction == "up":
            self.coord[1] -= self.speed
            self.coord[3] -= self.speed
        elif direction == "down":
            self.coord[1] += self.speed
            self.coord[3] += self.speed

    def set_direction(self, direction):
        self.prev_direction = direction
    
    def box_update(self):
        self.canvas.coords(
            self.box,
            self.coord[0],
            self.coord[1],
            self.coord[2],
            self.coord[3]
        )
        if self.vision_circle is not None:
            self.canvas.coords(
                self.vision_circle,
                self.center[0] - self.vision_range,
                self.center[1] - self.vision_range,
                self.center[0] + self.vision_range,
                self.center[1] + self.vision_range
            )
        self.corners = [
            (self.coord[0], self.coord[1]),  # top-left
            (self.coord[2], self.coord[1]),  # top-right
            (self.coord[0], self.coord[3]),  # bottom-left
            (self.coord[2], self.coord[3])   # bottom-right
        ]
        self.center = ((self.coord[0] + self.coord[2]) / 2, (self.coord[1] + self.coord[3]) / 2)

    def change_color(self, color):
        self.canvas.itemconfig(self.box, fill=color)

    def toggle_manual_control(self):
        self.manual_control = not self.manual_control
        if self.manual_control:
            self.change_color("yellow")
        else:
            self.change_color(self.default_color)
    
    @staticmethod
    def choose_direction(box, inertia_probability = 0.95):
        if random.random() > inertia_probability:
            return random.choice(box.possible_directions)
        else:
            return box.prev_direction
    
    @staticmethod
    def check_box_collision(box1, box2, direction):
        if direction == "up":
            return ((box2.coord[0] < box1.coord[0] and box1.coord[0] < box2.coord[2]) or \
                    (box2.coord[0] < box1.coord[2] and box1.coord[2] < box2.coord[2]) or\
                    (box2.coord[0] == box1.coord[0] and box1.coord[2] == box2.coord[2]) or\
                    (box1.coord[0] <= box2.coord[0] and box1.coord[2] >= box2.coord[2])) and \
                    box1.coord[1] - box1.speed < box2.coord[3] and \
                    box1.coord[3] > box2.coord[1]
                    
        elif direction == "down":
            return ((box2.coord[0] < box1.coord[0] and box1.coord[0] < box2.coord[2]) or \
                    (box2.coord[0] < box1.coord[2] and box1.coord[2] < box2.coord[2]) or \
                    (box2.coord[0] == box1.coord[0] and box1.coord[2] == box2.coord[2])or \
                    (box1.coord[0] <= box2.coord[0] and box1.coord[2] >= box2.coord[2])) and \
                    box1.coord[3] + box1.speed > box2.coord[1] and \
                    box1.coord[1] < box2.coord[3]
        
        elif direction == "left":
            return ((box2.coord[1] < box1.coord[1] and box1.coord[1] < box2.coord[3]) or \
                    (box2.coord[1] < box1.coord[3] and box1.coord[3] < box2.coord[3]) or \
                    (box2.coord[1] == box1.coord[1] and box1.coord[3] == box2.coord[3]) or \
                    (box1.coord[1] <= box2.coord[1] and box1.coord[3] >= box2.coord[3])) and \
                    box1.coord[0] - box1.speed < box2.coord[2] and \
                    box1.coord[2] > box2.coord[0]
        
        elif direction == "right":
            return ((box2.coord[1] < box1.coord[1] and box1.coord[1] < box2.coord[3]) or \
                    (box2.coord[1] < box1.coord[3] and box1.coord[3] < box2.coord[3]) or \
                    (box2.coord[1] == box1.coord[1] and box1.coord[3] == box2.coord[3]) or \
                    (box1.coord[1] <= box2.coord[1] and box1.coord[3] >= box2.coord[3])) and \
                    box1.coord[2] + box1.speed > box2.coord[0] and \
                    box1.coord[0] < box2.coord[2]
        
        else: return False
    
    @staticmethod
    def check_screen_border_collision(box, direction, width, height):
        if direction == "up":
            return box.coord[1] - box.speed < 0
        elif direction == "down":
            return box.coord[3] + box.speed > height
        elif direction == "left":
            return box.coord[0] - box.speed < 0
        elif direction == "right":
            return box.coord[2] + box.speed > width

    @staticmethod
    def check_boxes_overlap(box1, box2):
        ''' Check if the two boxes are currently overlapping '''
        return (
            Box.check_box1_corners_inside_box2(box1, box2) or
            Box.check_box1_corners_inside_box2(box2, box1)
        )
    
    @staticmethod
    def check_box1_border_inside_box2(box1, box2):
        ''' Check if box1's borders are inside box2 '''
        return (
            (Box.check_point_inside_box(box2, box1.coord[0], box1.coord[1]) and
            Box.check_point_inside_box(box2, box1.coord[2], box1.coord[1])
            ) or \
            (Box.check_point_inside_box(box2, box1.coord[0], box1.coord[1]) and
            Box.check_point_inside_box(box2, box1.coord[2], box1.coord[1])
            ) or \
            (Box.check_point_inside_box(box2, box1.coord[0], box1.coord[3]) and
            Box.check_point_inside_box(box2, box1.coord[2], box1.coord[3])
            ) or \
            (Box.check_point_inside_box(box2, box1.coord[0], box1.coord[3]) and
            Box.check_point_inside_box(box2, box1.coord[2], box1.coord[3]))
        )

    @staticmethod
    def check_box1_corners_inside_box2(box1, box2):
        ''' Check if the two boxes are currently overlapping '''
        return (
            Box.check_point_inside_box(box2, box1.corners[0]) or
            Box.check_point_inside_box(box2, box1.corners[1]) or
            Box.check_point_inside_box(box2, box1.corners[2]) or
            Box.check_point_inside_box(box2, box1.corners[3])
        )
    
    @staticmethod
    def check_point_inside_box(box, point: tuple):
        ''' Check if a point (x,y) is inside the box '''
        x, y = point
        return (
            (box.coord[0] <= x <= box.coord[2]) and (box.coord[1] <= y <= box.coord[3])
        )

    def eat_food(self):
        self.change_dimensions(self.width + 2, self.height + 2)
        self.score += 1

    def un_growth(self):
        self.change_dimensions(self.width - 2, self.height - 2)
    
    def change_dimensions(self, new_width, new_height):
        # TODO: Center the box when changing dimensions
        if new_width <= self.growth_width_limit:
            self.width = new_width
            self.coord[2] = self.coord[0] + self.width
        if new_height <= self.growth_height_limit:
            self.height = new_height
            self.coord[3] = self.coord[1] + self.height
        self.box_update()
        