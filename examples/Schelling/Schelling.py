'''
Schelling Segregation Model
=========================================

A simple implementation of a Schelling segregation model.

This version demonstrates the ASCII renderer.
To use, run this code from the command line, e.g.
    $ ipython -i Schelling.py

viz is the visualization wrapper around
To print the current state of the model:
    viz.render()

To advance the model by one step and print the new state:
    viz.step()

To advance the model by e.g. 10 steps and print the new state:
    viz.step_forward(10)
'''

from __future__ import division # For Python 2.x compatibility
import random

import random

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector

from mesa.visualization.TextServer import TextServer

from mesa.visualization.TextVisualization import *

class SchellingModel(Model):
    '''
    Model class for the Schelling segregation model.
    '''

    def __init__(self, height, width, density, minority_pc, homophily):
        '''
        '''

        self.height = height
        self.width = width
        self.density = density
        self.minority_pc = minority_pc
        self.homophily = homophily

        self.schedule = RandomActivation(self)
        self.grid = Grid(height, width, torus=True)

        self.happy = 0
        self.datacollector = DataCollector(
            {"happy": lambda m: m.happy}, # Model-level count of happy agents
            # For testing purposes, agent's individual x and y
            {"x": lambda a: a.x, "y": lambda a: a.y}) 

        self.running = True

        # Set up agents
        for x in range(self.width):
            for y in range(self.height):
                if random.random() < self.density:
                    if random.random() < self.minority_pc:
                        agent_type = 1
                    else:
                        agent_type = 0

                    agent = SchellingAgent((x,y), x, y, agent_type)
                    self.grid[y][x] = agent
                    self.schedule.add(agent)

    def get_empty(self):
        '''
        Get a list of coordinate tuples of currently-empty cells.
        '''
        empty_cells = []
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[y][x] is None:
                    empty_cells.append((x, y))
        return empty_cells

    def step(self):
        '''
        Run one step of the model. If All agents are happy, halt the model.
        '''
        self.happy = 0 # Reset counter of happy agents
        self.schedule.step()
        self.datacollector.collect(self)

        if self.happy == self.schedule.get_agent_count():
            self.running = False

class SchellingAgent(Agent):
    '''
    Schelling segregation agent
    '''
    def __init__(self, unique_id, x, y, agent_type):
        '''
         Create a new Schelling agent.

         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        '''
        self.unique_id = unique_id
        self.x = x
        self.y = y
        self.type = agent_type

    def step(self, model):
        neighbors = model.grid.get_neighbors(self.x, self.y, moore=True)
        similar = 0
        for neighbor in neighbors:
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < model.homophily:
            new_x, new_y = random.choice(model.get_empty())
            model.grid[self.y][self.x] = None
            model.grid[new_y][new_x] = self
            self.x = new_x
            self.y = new_y
        else:
            model.happy += 1


class SchellingTextVisualization(TextVisualization):
    '''
    ASCII visualization for schelling model
    '''

    def __init__(self, model):
        '''
        Create new Schelling ASCII visualization.
        '''
        self.model = model

        grid_viz = TextGrid(self.model.grid, self.ascii_agent)
        happy_viz = TextData(self.model, 'happy')
        self.elements = [grid_viz, happy_viz]

    @staticmethod
    def ascii_agent(a):
        '''
        Minority agents are X, Majority are O.
        '''
        if a.type == 0:
            return 'O'
        if a.type == 1:
            return 'X'


if __name__ == "__main__":
    server = TextServer(SchellingModel, SchellingTextVisualization, "Schelling",
                        10, 10, 0.8, 0.2, 3)
    server.launch()
    #model = SchellingModel(10, 10, 0.8, 0.2, 3)
    #viz = SchellingTextVisualization(model)




