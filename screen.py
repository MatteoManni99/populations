import random
import tkinter as tk
from box import Box

class MyScreen:
    def __init__(self, config):
        self.config = config
        self.root = tk.Tk()
        self.root.title("Tkinter Moving Box")
        self.canvas = tk.Canvas(
            self.root,
            width=self.config["width"],
            height=self.config["height"],
            bg="white")
        self.width = self.config["width"]
        self.height = self.config["height"]
        self.canvas.pack()
        self.box_index = 0
        self.box_list = []
        for i in range(self.config["num_boxes"]):
            self.box_list.append(Box(self.canvas, i*40, i*10, self.config))

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.directions = ["up", "down", "left", "right"]
        self.config_colors = self.config["colors"]
        self.update()

    def key_press(self, event):
        key = event.keysym.lower()

        if key == "1": self.box_index = 0  # Select first box
        elif key == "2": self.box_index = 1  # Select second box
        elif key == "3": self.box_index = 2  # Select third box
        elif key == "escape": self.root.quit()  # Exit on Escape key

        if key == "d":
            if self.check_collisions("right", self.box_index) is False:
                self.box_list[self.box_index].move("right")
        elif key == "a":
            if self.check_collisions("left", self.box_index) is False:
                self.box_list[self.box_index].move("left")
        elif key == "s":
            if self.check_collisions("down", self.box_index) is False:
                self.box_list[self.box_index].move("down")
        elif key == "w":
            if self.check_collisions("up", self.box_index) is False:
                self.box_list[self.box_index].move("up")

        
    def key_release(self, event):
        key = event.keysym.lower()
        # if key in ["a", "d"]: self.box_list[self.box_index].dx = 0
        # if key in ["w", "s"]: self.box_list[self.box_index].dy = 0

    def update(self):
        for i, box in enumerate(self.box_list):
            direction = self.choose_direction(box)
            if self.check_collisions(direction, i) is False:
                box.move(direction)
            else:
                box.change_color(random.choice(self.config_colors))
            box.update()

        self.root.after(10, self.update) #(ms = , funztion = self.update)

    def run(self):
        self.root.mainloop()

    def check_collisions(self, direction, box_index):
        collision = False
        for i, box in enumerate(self.box_list):
            if i != box_index:
                collision |= self.check_collision(self.box_list[box_index], box, direction)
                if collision: break

        return collision
    
    def check_collision(self, box1, box2, direction):
        if direction == "up":
            return ((box2.corners[0] < box1.corners[0] and box1.corners[0] < box2.corners[2]) or \
                    (box2.corners[0] < box1.corners[2] and box1.corners[2] < box2.corners[2]) or\
                    (box2.corners[0] == box1.corners[0] and box1.corners[2] == box2.corners[2])) and \
                    box1.corners[1] - box1.speed < box2.corners[3] and \
                    box1.corners[3] > box2.corners[1] or \
                    box1.corners[1] - box1.speed < 0
        elif direction == "down":
            return ((box2.corners[0] < box1.corners[0] and box1.corners[0] < box2.corners[2]) or \
                    (box2.corners[0] < box1.corners[2] and box1.corners[2] < box2.corners[2]) or \
                    (box2.corners[0] == box1.corners[0] and box1.corners[2] == box2.corners[2])) and \
                    box1.corners[3] + box1.speed > box2.corners[1] and \
                    box1.corners[1] < box2.corners[3] or \
                    box1.corners[3] + box1.speed > self.height
        elif direction == "left":
            return ((box2.corners[1] < box1.corners[1] and box1.corners[1] < box2.corners[3]) or \
                    (box2.corners[1] < box1.corners[3] and box1.corners[3] < box2.corners[3]) or \
                    (box2.corners[1] == box1.corners[1] and box1.corners[3] == box2.corners[3])) and \
                    box1.corners[0] - box1.speed < box2.corners[2] and \
                    box1.corners[2] > box2.corners[0] or \
                    box1.corners[0] - box1.speed < 0
        elif direction == "right":
            return ((box2.corners[1] < box1.corners[1] and box1.corners[1] < box2.corners[3]) or \
                    (box2.corners[1] < box1.corners[3] and box1.corners[3] < box2.corners[3]) or \
                    (box2.corners[1] == box1.corners[1] and box1.corners[3] == box2.corners[3])) and \
                    box1.corners[2] + box1.speed > box2.corners[0] and \
                    box1.corners[0] < box2.corners[2] or \
                    box1.corners[2] + box1.speed > self.width
        return False

    def choose_direction(self, box):
        if box.prev_direction is None:
            return random.choice(self.directions)
        elif random.random() > 0.95:
            return random.choice(self.directions)
        else:
            return box.prev_direction