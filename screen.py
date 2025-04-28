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
            print("canva type", type(self.canvas))
            self.box_list.append(Box(self.canvas, i*100, i*10, self.config))

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.update()

    def key_press(self, event):
        key = event.keysym.lower()
        
        speed = self.config["speed"]
    
        if key == "d":
            self.box_list[self.box_index].dx = speed
        elif key == "a":
            self.box_list[self.box_index].dx = -speed
        elif key == "s":
            self.box_list[self.box_index].dy = speed
        elif key == "w":
            self.box_list[self.box_index].dy = -speed

        restrictions = self.check_collisions()
        print("restrictions", restrictions)
        if "right" in restrictions or "left" in restrictions:
            self.box_list[self.box_index].dx = 0
        if "up" in restrictions or "down" in restrictions:
            self.box_list[self.box_index].dy = 0
        if key == "1": self.box_index = 0  # Select first box
        elif key == "2": self.box_index = 1  # Select second box
        elif key == "3": self.box_index = 2  # Select third box
        elif key == "escape": self.root.quit()  # Exit on Escape key

    def key_release(self, event):
        key = event.keysym.lower()
        if key in ["a", "d"]: self.box_list[self.box_index].dx = 0
        if key in ["w", "s"]: self.box_list[self.box_index].dy = 0
    
    # def key_press(self, event):
    #     if event.keysym == "Right": self.dx = 5
    #     elif event.keysym == "Left": self.dx = -5
    #     elif event.keysym == "Down": self.dy = 5
    #     elif event.keysym == "Up": self.dy = -5

    # def key_release(self, event):
    #     if event.keysym in ["Right", "Left"]: self.dx = 0
    #     if event.keysym in ["Up", "Down"]: self.dy = 0

    def update(self):
        for box in self.box_list:
            box.move()
        
        self.root.after(16, self.update) # ~60 FPS

    def run(self):
        self.root.mainloop()

    def check_collisions(self):
        restrictions = []
        for i in range(len(self.box_list)):
            if i != self.box_index:
                restrictions += self.check_collision(self.box_list[self.box_index], self.box_list[i])

        return restrictions
    
    def check_collision(self, box1, box2):
        restrictions = []
        #futura collisione a destra
        if (box1.corners[0][0] + box1.dx + box1.width >= box2.corners[0][0] and
            box1.corners[0][1] + box1.dy <= box2.corners[0][1] + box2.height and
            box1.corners[0][1] + box1.dy + box1.height >= box2.corners[0][1]):
            restrictions.append("right")
        #futura collisione a sinistra
        if (box1.corners[0][0] + box1.dx <= box2.corners[0][0] + box2.width and
            box1.corners[0][1] + box1.dy <= box2.corners[0][1] + box2.height and
            box1.corners[0][1] + box1.dy + box1.height >= box2.corners[0][1]):
            restrictions.append("left")
        #futura collisione in alto
        if (box1.corners[0][0] + box1.dx <= box2.corners[0][0] + box2.width and
            box1.corners[0][1] + box1.dy <= box2.corners[0][1] + box2.height and
            box1.corners[0][1] + box1.dy + box1.height >= box2.corners[0][1]):
            restrictions.append("up")
        #futura collisione in basso
        if (box1.corners[0][0] + box1.dx + box1.width >= box2.corners[0][0] and
            box1.corners[0][1] + box1.dy <= box2.corners[0][1] + box2.height and
            box1.corners[0][1] + box1.dy + box1.height >= box2.corners[0][1]):
            restrictions.append("down")
            
        return restrictions
    