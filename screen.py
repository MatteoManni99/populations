import time
import tkinter as tk
from box import Box
from food import Food

class MyScreen:
    def __init__(self, config):
        self.config = config
        print("Good time settings: ", self.good_time_settings())
        print("Good size settings: ", self.good_size_settings())

        self.root = tk.Tk()
        self.root.title("Populations")
        padding = 1
        self.root.geometry(str(self.config["world_width"] + self.config["dashboard_width"] + padding*2) + "x" + str(self.config["world_height"] + padding*3) + "+100+50")
        self.root.resizable(False, False)

        dashboard_frame = tk.Frame(
            self.root,
            width=self.config["dashboard_width"],
            bg="black",
            highlightthickness=0
        )
        dashboard_frame.pack(side="left", fill="y")
        dashboard_canvas = tk.Canvas(
            dashboard_frame,
            bg="lightgrey",
            width=self.config["dashboard_width"],
            height=self.config["dashboard_height"],
            highlightthickness=0  # rimuove bordo grigio predefinito di Tkinter
        )
        dashboard_canvas.pack(
            padx=(padding, 0),
            pady=(padding, padding)
        )

        world_frame = tk.Frame(
            self.root,
            bg="black",
            highlightthickness=0
        )
        world_frame.pack(side="left", fill="both", expand=True)
        self.world_canvas = tk.Canvas(
            world_frame,
            bg="white",
            width=self.config["world_width"],
            height=self.config["world_height"],
            highlightthickness=0  # rimuove bordo grigio predefinito di Tkinter
        )
        self.world_canvas.pack(padx=padding, pady=padding)

        self.box_list = []
        for i in range(self.config["num_boxes"]):
            self.box_list.append(Box(self.world_canvas, i*40, i*10, self.config, self.config["box"]))
        self.food_list = []

        self.world_canvas.bind("<Button-1>", self.on_left_click)
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

        self.possible_directions = config["possible_directions"]
        self.config_colors = self.config["colors"]
        self.random_walk = self.config["box_random_walk"]
        self.spawn_food_event = self.config["spawn_food_event"]
        self.last_update_time_spawn_food = time.time()
        self.last_update_time_move = time.time()
        self.manual_control_one_box = False
        self.box_manual_control_index = 0  # Index of the box under manual control
        self.box_monitored_index = None  # Index of the box being monitored
        self.paused = False

        # Dashboard info labels
        self.box_monitored_index_var = tk.StringVar(value="None")
        self.box_monitored_score_var = tk.StringVar(value="None")
        self.box_monitored_view_box_var = tk.StringVar(value="None")
        self.box_monitored_view_food_var = tk.StringVar(value="None")
        info_frame = tk.Frame(dashboard_frame, bg="white", highlightbackground="black", highlightthickness=1)
        info_frame.place(x=10, y=10)  # posizione dentro il dashboard_canvas
        tk.Label(info_frame, text="Box Index:", bg="white", anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(info_frame, textvariable=self.box_monitored_index_var, bg="white", anchor="w").grid(row=0, column=1, sticky="w")
        tk.Label(info_frame, text="Score:", bg="white", anchor="w").grid(row=1, column=0, sticky="w")
        tk.Label(info_frame, textvariable=self.box_monitored_score_var, bg="white", anchor="w").grid(row=1, column=1, sticky="w")
        tk.Label(info_frame, text="View Box:", bg="white", anchor="w").grid(row=2, column=0, sticky="w")
        tk.Label(info_frame, textvariable=self.box_monitored_view_box_var, bg="white", anchor="w").grid(row=2, column=1, sticky="w")
        tk.Label(info_frame, text="View Food:", bg="white", anchor="w").grid(row=3, column=0, sticky="w")
        tk.Label(info_frame, textvariable=self.box_monitored_view_food_var, bg="white", anchor="w").grid(row=3, column=1, sticky="w")
        
        self.update()
        
    def on_left_click(self, event):
        x, y = event.x, event.y
        # Check if the click was inside the box
        for box in self.box_list:
            if Box.check_point_inside_box(box, (x, y)):
                if self.box_monitored_index is not None:
                    # Unhighlight previously monitored box
                    self.box_list[self.box_monitored_index].set_highlight(False)
                    self.dashboard_box_highlight_clean()
                # Highlight new monitored box
                box.set_highlight(True)
                self.box_monitored_index = self.box_list.index(box)
                return

        # if click was outside any box reset monitored box if any
        if self.box_monitored_index is not None:
            self.box_list[self.box_monitored_index].set_highlight(False)
            self.dashboard_box_highlight_clean()
            self.box_monitored_index = None

    def key_press(self, event):
        key = event.keysym.lower()

        if key == "space": self.paused = not self.paused  # Toggle pause
        if key == "m":
            self.manual_control_one_box = not self.manual_control_one_box  # Toggle manual control
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

        if self.box_monitored_index is not None:
            #Update dashboard info
            self.box_monitored_index_var.set(str(self.box_monitored_index))
            self.box_monitored_score_var.set(str(self.box_list[self.box_monitored_index].score))
            self.box_monitored_view_box_var.set(str(len(self.box_list[self.box_monitored_index].box_in_vision)))
            self.box_monitored_view_food_var.set(str(len(self.box_list[self.box_monitored_index].food_in_vision)))

        if self.spawn_food_event:
            #Spawn food randomly
            elapsed = time.time() - self.last_update_time_spawn_food
            if elapsed >= self.config["food"]["spawn_rate_ms"]/1000:
                self.last_update_time_spawn_food = time.time()
                if len(self.food_list) < self.config["food"]["max_food_items"]:
                    food = Food.spawn_food_event(self.world_canvas, self.config)
                    self.food_list.append(food)

        if self.random_walk:
            #Move boxes randomly
            elapsed = time.time() - self.last_update_time_move
            if elapsed >= self.config["box"]["move_rate_ms"]/1000:
                self.last_update_time_move = time.time()
                
                #Move boxes
                for i, box in enumerate(self.box_list):
                    if self.manual_control_one_box and i == self.box_manual_control_index:
                        continue

                    direction = Box.choose_direction(box, inertia_probability=0.95)
                    if self.check_collisions_post_move(direction, i) is False:
                        box.move(direction)
                    else:
                        # Collision detected, choose a new direction
                        new_direction = Box.choose_direction(box, inertia_probability=0.0)
                        box.set_direction(new_direction)
                    box.box_update()
                
                #Try to eat food
                for i, box in enumerate(self.box_list):
                    self.try_eat_food(box_index = i)
                
                #Update elements in vision
                for box in self.box_list:
                    box.update_elements_in_vision(self.food_list, self.box_list)

        self.root.after(ms = self.config["ms_between_frames"], func = self.update) #(ms = , funztion = self.update)

    def dashboard_box_highlight_clean(self):
        self.box_monitored_index_var.set("None")
        self.box_monitored_score_var.set("None")
        self.box_monitored_view_box_var.set("None")
        self.box_monitored_view_food_var.set("None")

    def run(self):
        self.root.mainloop()

    def check_collisions_post_move(self, direction, box_index):
        collision = False
        collision |= Box.check_screen_border_collision(self.box_list[box_index], direction, self.config["world_width"], self.config["world_height"])
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
                self.world_canvas.delete(food.box)
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
    
    def good_size_settings(self):
        return (
            self.config["world_height"] == self.config["dashboard_height"]
        )
    

    