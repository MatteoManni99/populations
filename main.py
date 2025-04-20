import json
from screen import MyScreen

with open('config.json', 'r') as file:
    config = json.load(file)
    app = MyScreen(config)
    app.run()