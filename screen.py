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
        self.canvas.pack()
        self.box_index = 0
        self.box_list = []
        for i in range(self.config["num_boxes"]):
            self.box_list.append(Box(self.canvas, i*100, i*10, self.config))

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.update()


    def key_press(self, event):
        key = event.keysym.lower()

        if key == "1": self.box_index = 0  # Select first box
        elif key == "2": self.box_index = 1  # Select second box
        elif key == "3": self.box_index = 2  # Select third box
        elif key == "escape": self.root.quit()  # Exit on Escape key

        if key == "d":
            if self.check_collisions("right") is False:
                self.box_list[self.box_index].move("right")
        elif key == "a":
            if self.check_collisions("left") is False:
                self.box_list[self.box_index].move("left")
        elif key == "s":
            if self.check_collisions("down") is False:
                self.box_list[self.box_index].move("down")
        elif key == "w":
            if self.check_collisions("up") is False:
                self.box_list[self.box_index].move("up")

        
    def key_release(self, event):
        key = event.keysym.lower()
        # if key in ["a", "d"]: self.box_list[self.box_index].dx = 0
        # if key in ["w", "s"]: self.box_list[self.box_index].dy = 0

    def update(self):
        for box in self.box_list:
            box.update()

        self.root.after(16, self.update) # ~60 FPS

    def run(self):
        self.root.mainloop()

    def check_collisions(self, direction):
        collision = False
        for i in range(len(self.box_list)):
            if i != self.box_index:
                collision |= self.check_collision(self.box_list[self.box_index], self.box_list[i], direction)
                if collision: break

        return collision
    
    def check_collision(self, box1, box2, direction):
        if direction == "up":
            return ((box2.corners[0] < box1.corners[0] and box1.corners[0] < box2.corners[2]) or \
                    (box2.corners[0] < box1.corners[2] and box1.corners[2] < box2.corners[2]) or\
                    (box2.corners[0] == box1.corners[0] and box1.corners[2] == box2.corners[2])) and \
                    box1.corners[1] - box1.speed < box2.corners[3] and \
                    box1.corners[3] > box2.corners[1]
        elif direction == "down":
            return ((box2.corners[0] < box1.corners[0] and box1.corners[0] < box2.corners[2]) or \
                    (box2.corners[0] < box1.corners[2] and box1.corners[2] < box2.corners[2]) or \
                    (box2.corners[0] == box1.corners[0] and box1.corners[2] == box2.corners[2])) and \
                    box1.corners[3] + box1.speed > box2.corners[1] and \
                    box1.corners[1] < box2.corners[3]
        elif direction == "left":
            return ((box2.corners[1] < box1.corners[1] and box1.corners[1] < box2.corners[3]) or \
                    (box2.corners[1] < box1.corners[3] and box1.corners[3] < box2.corners[3]) or \
                    (box2.corners[1] == box1.corners[1] and box1.corners[3] == box2.corners[3])) and \
                    box1.corners[0] - box1.speed < box2.corners[2] and \
                    box1.corners[2] > box2.corners[0]
        elif direction == "right":
            return ((box2.corners[1] < box1.corners[1] and box1.corners[1] < box2.corners[3]) or \
                    (box2.corners[1] < box1.corners[3] and box1.corners[3] < box2.corners[3]) or \
                    (box2.corners[1] == box1.corners[1] and box1.corners[3] == box2.corners[3])) and \
                    box1.corners[2] + box1.speed > box2.corners[0] and \
                    box1.corners[0] < box2.corners[2]
        return False