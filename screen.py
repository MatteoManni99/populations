import random
import time
import tkinter as tk
from box import Box
from food import Food

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
        self.food_list = []
        for i in range(self.config["num_boxes"]):
            self.box_list.append(Box(self.canvas, i*40, i*10, self.config, self.config["box"]))

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.possible_directions = config["possible_directions"]
        self.config_colors = self.config["colors"]
        self.random_walk = self.config["box_random_walk"]
        print("Random walk:", self.random_walk)
        self.last_update_time_spawn_food = time.time()
        self.last_update_time_move = time.time()
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
        
        ## Auto-move boxes, 1 move every frame (update) ##
        if self.random_walk:
            elapsed = time.time() - self.last_update_time_move
            if elapsed >= self.config["box"]["move_rate_sec"]:
                self.last_update_time_move = time.time()
                for i, box in enumerate(self.box_list):
                    direction = Box.choose_direction(box, inertia_probability=0.95)
                    if self.check_collisions(direction, i) is False:
                        box.move(direction)
                    else:
                        # Collision detected, choose a new direction
                        new_direction = Box.choose_direction(box, inertia_probability=0.0)
                        if self.check_collisions(new_direction, i) is False:
                            box.move(new_direction)
                    box.update()
            
        #Spawn food randomly
        elapsed = time.time() - self.last_update_time_spawn_food
        if elapsed >= self.config["food"]["spawn_rate_sec"]:
            self.last_update_time_spawn_food = time.time()
            food = Food.spawn_food_event(self.canvas, self.config)
            self.food_list.append(food)

        self.root.after(self.config["ms_between_frames"], self.update) #(ms = , funztion = self.update)

    def run(self):
        self.root.mainloop()

    def check_collisions(self, direction, box_index):
        collision = False
        collision |= Box.check_border_collision(self.box_list[box_index], direction, self.width, self.height)
        for i, box in enumerate(self.box_list):
            if i != box_index:
                collision |= Box.check_box_collision(self.box_list[box_index], box, direction)  
                if collision: break
        
        #TODO: rimuovere il rischio che post mangiata il box si trovi dentro un altro box
        if collision is False:
            # Check food collisions
            #TODO: the box should eat multiple food items in one move
            for i, food in enumerate(self.food_list):
                if Box.check_box_collision(self.box_list[box_index], food, direction):
                    self.box_list[box_index].eat_food()
                    self.canvas.delete(food.box)
                    del self.food_list[i]
                    break

        return collision
    
    

    