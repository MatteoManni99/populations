import json

import torch
from screen import MyScreen
from brain import FCClassifier


with open('config.json', 'r') as file:
    config = json.load(file)
    
    # net = FCClassifier([17, 5, 4], activations = ["relu", "softmax"], bias=True, init="xavier")
    
    # print(net(torch.ones(1, 17)))
    # print(net.predict(torch.ones(1, 17)))
    # print(net.predict(torch.randn(1, 17)))
    
    app = MyScreen(config)
    app.run()