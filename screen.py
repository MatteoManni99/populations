import tkinter as tk

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

        self.x, self.y = 50, 50
        self.box = self.canvas.create_rectangle(self.x, self.y, self.x + 50, self.y + 50, fill="red")

        self.dx = 0
        self.dy = 0

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.update()

    def key_press(self, event):
        key = event.keysym.lower()
        if key == "d": self.dx = self.config["speed"]
        elif key == "a": self.dx = -self.config["speed"]
        elif key == "s": self.dy = self.config["speed"]
        elif key == "w": self.dy = -self.config["speed"]
        elif key == "escape": self.root.quit()  # Exit on Escape key

    def key_release(self, event):
        key = event.keysym.lower()
        if key in ["a", "d"]: self.dx = 0
        if key in ["w", "s"]: self.dy = 0
    
    # def key_press(self, event):
    #     if event.keysym == "Right": self.dx = 5
    #     elif event.keysym == "Left": self.dx = -5
    #     elif event.keysym == "Down": self.dy = 5
    #     elif event.keysym == "Up": self.dy = -5

    # def key_release(self, event):
    #     if event.keysym in ["Right", "Left"]: self.dx = 0
    #     if event.keysym in ["Up", "Down"]: self.dy = 0

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.canvas.coords(self.box, self.x, self.y, self.x + 50, self.y + 50)
        self.root.after(16, self.update)  # ~60 FPS

    def run(self):
        self.root.mainloop()