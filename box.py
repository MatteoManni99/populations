import random
import torch
import brain as brn
from utils import normalize_coord, normalize_coords

class Box:
    def __init__(self, canvas, x_world, y_world, config, config_box, brain=None):
        self.config = config
        self.config_box = config_box
        self.width = config_box["width"]
        self.height = config_box["height"]
        self.growth_width_limit = config_box["growth_width_limit"]
        self.growth_height_limit = config_box["growth_height_limit"]
        self.vision_range = config_box["vision_range"]
        self.canvas = canvas
        self.coord = [x_world, y_world, x_world + self.width, y_world + self.height]
        self.center = ((self.coord[0] + self.coord[2]) / 2, (self.coord[1] + self.coord[3]) / 2)
        self.box = canvas.create_rectangle(
            self.coord[0],
            self.coord[1],
            self.coord[2],
            self.coord[3],
            fill=self.config_box["color"]
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
        self.highlighted = False
        self.speed = config_box["speed"]
        self.possible_directions = config["possible_directions"]
        self.prev_direction = random.choice(self.possible_directions)
        self.score = 0
        self.energy = float(config_box["initial_energy"])
        self.box_in_vision = []  # List of boxes currently in vision
        self.food_in_vision = []  # List of food currently in vision
        if config_box["use_nn_brain"]:
            if brain is not None:
                self.brain = brain
            else:
                self.brain = brn.FCClassifier(
                    layer_sizes=config_box["nn_brain_structure"]["layers"],
                    activations=config_box["nn_brain_structure"]["activations"],
                    bias=config_box["nn_brain_structure"]["bias"],
                    init=config_box["nn_brain_structure"]["init"]
            )

    def choose_direction(self, inertia_probability = 0.95, direction=None):
        if direction is None:
            if (self.config_box["use_nn_brain"]):
                # Use neural network to choose direction based on position of nearest food and boxes
                list_of_inputs = []
                list_of_inputs.extend(normalize_coords(self.center[0], self.center[1], self.config["world_width"], self.config["world_height"]))  # Normalized x,y position
                
                # Nearest food
                for i in range(self.config_box["number_of_food_that_brain_can_manage"]):
                    if i < len(self.food_in_vision):
                        food = self.food_in_vision[i]["food"]
                        # Lower distance means higher input value
                        list_of_inputs.append(1 / (self.food_in_vision[i]["distance"]/self.vision_range))  # Normalized vicinity
                        # Normalized position
                        list_of_inputs.extend(normalize_coords(food.center[0], food.center[1], self.config["world_width"], self.config["world_height"]))  # Normalized x,y position
                    else:
                        # No food available, fill with max vicinity and zero position. Neural network should learn to ignore these.
                        list_of_inputs.append(0.0)
                        list_of_inputs.extend([0.0, 0.0])
                
                input_tensor = torch.tensor([list_of_inputs], dtype=torch.float32)
                output = self.brain.predict(input_tensor)
                direction_index = output.item()
                return self.possible_directions[direction_index]
            
            elif random.random() > inertia_probability:
                return random.choice(self.possible_directions)
            else:
                return self.prev_direction
        else:
            return direction
        
    def move(self, direction):
        self.energy -= self.config_box["move_energy_cost"]

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

        #TODO: create a dedicated method for brain mutation
        if (self.config_box["use_nn_brain"] and self.config_box["brain_mutations"]):
                # Mutate brain post move
                for param in self.brain.parameters():
                    if random.random() < self.config_box["brain_mutation_rate_post_move"]:
                        noise = torch.randn_like(param) * self.config_box["brain_mutation_coefficient"]
                        param.data.add_(noise)

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
    
    def damage_energy(self, amount):
        self.energy -= amount

    def update_elements_in_vision(self, food_list, box_list):
        # Update food in vision
        self.food_in_vision = []
        for food in food_list:
            distance = ((self.center[0] - food.center[0]) ** 2 + (self.center[1] - food.center[1]) ** 2) ** 0.5
            if distance <= self.vision_range:
                self.food_in_vision.append({"distance": distance, "food": food})
        
        # Update boxes in vision
        self.box_in_vision = []
        for box in box_list:
            if box is self:
                continue
            distance = ((self.center[0] - box.center[0]) ** 2 + (self.center[1] - box.center[1]) ** 2) ** 0.5
            if distance <= self.vision_range:
                self.box_in_vision.append({"distance": distance, "box": box})
    
    def order_elements_in_vision_by_distance(self):
        self.food_in_vision.sort(key=lambda x: x["distance"])
        self.box_in_vision.sort(key=lambda x: x["distance"])

    def change_color(self, color):
        self.canvas.itemconfig(self.box, fill=color)
    
    def kill(self):
        if self.vision_circle is not None:
            self.canvas.delete(self.vision_circle)
    
    def try_mithosis(self):
        if self.energy >= self.config_box["mithosis_energy_cost"]*2:
            if random.random() < self.config_box["mithosis_chance"]:
                self.energy -= self.config_box["mithosis_energy_cost"]
                return True
        return False

    def reset_color(self):
        if self.manual_control:
            self.change_color(self.config["box"]["manual_color"])
        elif self.highlighted:
            self.change_color(self.config["box"]["highlight_color"])
        else:
            self.change_color(self.config["box"]["color"])

    def toggle_manual_control(self):
        self.manual_control = not self.manual_control
        self.reset_color()

    def set_highlight(self, highlighted):
        self.highlighted = highlighted
        self.reset_color()

    
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
    def check_screen_border_collision(box, direction, world_width, world_height):
        if direction == "up":
            return box.coord[1] - box.speed < 0
        elif direction == "down":
            return box.coord[3] + box.speed > world_height
        elif direction == "left":
            return box.coord[0] - box.speed < 0
        elif direction == "right":
            return box.coord[2] + box.speed > world_width

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
        self.score += 10
        self.energy += self.config_box["energy_per_food"]

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
        