import numpy as np


class Tree:
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.childs = list()
        self.action = list()
        self.mean_value = 0.0
        self.max_value = -np.inf
        self.sum_squared_results = 0.0
        self.number_of_visits = 0.0
        self.end_node = False

    def append_node(self, child):
        self.childs.append(child)
        child.parent = self