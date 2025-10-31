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
        self.box_list = []
        self.food_list = []
        for i in range(self.config["num_boxes"]):
            self.box_list.append(Box(self.canvas, i*40, i*10, self.config, self.config["box"]))

        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.possible_directions = config["possible_directions"]
        self.config_colors = self.config["colors"]
        self.random_walk = self.config["box_random_walk"]
        self.spawn_food_event = self.config["spawn_food_event"]
        self.last_update_time_spawn_food = time.time()
        self.last_update_time_move = time.time()
        self.manual_control_one_box = False
        self.box_manual_control_index: int = 0  # Index of the box under manual control
        self.paused = False
        self.update()
        print("Good settings: ", self.good_time_settings())
    
    def key_press(self, event):
        key = event.keysym.lower()

        if key == "space": self.paused = not self.paused  # Toggle pause
        if key == "m":
            self.manual_control_one_box = not self.manual_control_one_box # Toggle manual control
            self.box_list[self.box_manual_control_index].toggle_manual_control()
        elif key == "escape": self.root.quit()  # Exit on Escape key
        
        if self.manual_control_one_box and not self.paused:
            if key == "d":
                if self.check_collisions_post_move("right", self.box_manual_control_index) is False:
                    self.box_list[self.box_manual_control_index].move("right")
            elif key == "a":
                if self.check_collisions_post_move("left", self.box_manual_control_index) is False:
                    self.box_list[self.box_manual_control_index].move("left")
            elif key == "s":
                if self.check_collisions_post_move("down", self.box_manual_control_index) is False:
                    self.box_list[self.box_manual_control_index].move("down")
            elif key == "w":
                if self.check_collisions_post_move("up", self.box_manual_control_index) is False:
                    self.box_list[self.box_manual_control_index].move("up")
                    
            self.try_eat_food(box_index = self.box_manual_control_index)
            self.box_list[self.box_manual_control_index].box_update()
            
    def key_release(self, event):
        key = event.keysym.lower()
        # if key in ["a", "d"]: self.box_list[self.box_index].dx = 0
        # if key in ["w", "s"]: self.box_list[self.box_index].dy = 0

    def update(self):
        if self.paused:
            self.root.after(ms = self.config["ms_between_frames"], func = self.update)
            return
        
        if self.spawn_food_event:
            #Spawn food randomly
            elapsed = time.time() - self.last_update_time_spawn_food
            if elapsed >= self.config["food"]["spawn_rate_ms"]/1000:
                self.last_update_time_spawn_food = time.time()
                if len(self.food_list) < self.config["food"]["max_food_items"]:
                    food = Food.spawn_food_event(self.canvas, self.config)
                    self.food_list.append(food)

        if self.random_walk:
            #Move boxes randomly
            elapsed = time.time() - self.last_update_time_move
            if elapsed >= self.config["box"]["move_rate_ms"]/1000:
                self.last_update_time_move = time.time()
                for i, box in enumerate(self.box_list):

                    if self.manual_control_one_box and i == self.box_manual_control_index:
                        continue
                    
                    #Move box
                    direction = Box.choose_direction(box, inertia_probability=0.95)
                    if self.check_collisions_post_move(direction, i) is False:
                        box.move(direction)
                    else:
                        # Collision detected, choose a new direction
                        new_direction = Box.choose_direction(box, inertia_probability=0.0)
                        box.set_direction(new_direction)
                    box.box_update()
                    
                    #Try to eat food
                    self.try_eat_food(box_index = i)        
        
        self.root.after(ms = self.config["ms_between_frames"], func = self.update) #(ms = , funztion = self.update)

    def run(self):
        self.root.mainloop()

    def check_collisions_post_move(self, direction, box_index):
        collision = False
        collision |= Box.check_screen_border_collision(self.box_list[box_index], direction, self.width, self.height)
        for i, box in enumerate(self.box_list):
            if i != box_index:
                collision |= Box.check_box_collision(self.box_list[box_index], box, direction)  
                if collision: break
        return collision
    
    def try_eat_food(self, box_index):
        collision_post_eating = False
        for i, food in enumerate(self.food_list):
            if Box.check_boxes_overlap(self.box_list[box_index], food):
                self.box_list[box_index].eat_food()
                self.canvas.delete(food.box)
                del self.food_list[i]
                for i, box in enumerate(self.box_list):
                    if i != box_index:
                        collision_post_eating |= Box.check_boxes_overlap(self.box_list[box_index], box)
                        if collision_post_eating:
                            self.box_list[box_index].un_growth()
                            break
                self.box_list[box_index].box_update()
        
    def good_time_settings(self):
        return (
            self.config["food"]["spawn_rate_ms"] % self.config["ms_between_frames"] == 0 and \
            self.config["food"]["spawn_rate_ms"] >= self.config["ms_between_frames"] and \
            self.config["box"]["move_rate_ms"] % self.config["ms_between_frames"] == 0 and \
            self.config["box"]["move_rate_ms"] >= self.config["ms_between_frames"] \
        )
    
    

    