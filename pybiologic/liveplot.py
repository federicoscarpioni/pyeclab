# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.animation as animation
import numpy as np
import time

class Liveplot():
    def __init__(self, channel):
        # Create figure for plotting
        self.fig = plt.figure(figsize=(12, 5))
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax2 = self.ax.twinx()
        self.initialize_arrays()
        self.line,  = self.ax.plot ([], [], '-', label = 'Voltage', color='C0')
        self.line2, = self.ax2.plot([], [], '-', label = 'Current', color='orange')
        self.ax.set_title(f'Channel {channel}')
    
    
    def initialize_arrays(self):
        self.time = np.array([])
        self.current = np.array([])
        self.voltage = np.array([])
    
    
    def get_queue(self):
        data = []
        while not self.q.empty():
            data.append(self.q.get())
        return data
    
    # This function is called periodically from FuncAnimation
    def animate(self, i, q):
        while not q[0].empty():
           self.voltage = np.append(self.voltage, q[0].get())
        while not q[1].empty():
            self.current = np.append(self.current, q[1].get())
        while not q[2].empty():
           self.time = np.append(self.time, q[2].get())

        # Queues are not of the same lenghts so the shortest is searched
        index_max1 = min(len(self.time), len(self.voltage)) 
        index_max2 = min(len(self.time), len(self.current)) 
        # After 120 second plot in minutes
        # After 90 minutes plot in hours
        if self.time[-1]>5400:
            self.line.set_data (self.time[0:index_max1]/3600, self.voltage[0:index_max1])
            self.line2.set_data(self.time[0:index_max2]/3600, self.current[0:index_max2])
            self.ax.set_xlabel('Time / hour', fontsize=16)
        # After 120 second plot in minutes
        elif self.time[-1]>120: 
            self.line.set_data (self.time[0:index_max1]/60, self.voltage[0:index_max1])
            self.line2.set_data(self.time[0:index_max2]/60, self.current[0:index_max2])
            self.ax.set_xlabel('Time / min', fontsize=16)
        # Plot in seconds
        else:
            self.line.set_data (self.time[0:index_max1], self.voltage[0:index_max1])
            self.line2.set_data(self.time[0:index_max2], self.current[0:index_max2])
            self.ax.set_xlabel('Time / sec', fontsize=16)
        self.ax.relim()
        self.ax2.relim()
        self.ax.autoscale_view()
        self.ax2.autoscale_view()
        # Plot options
        self.ax.set_ylabel('Potential (V)', color='C0', fontsize=16)
        self.ax2.set_ylabel('Current (A)', color='orange', fontsize=16)
        self.ax.tick_params(axis = 'x', which = 'both', top = False)
        self.ax.tick_params(axis = 'y', which = 'both', right = False, colors = 'C0')
        self.ax2.tick_params(axis = 'y', which = 'both', right = True, labelright = True, left = False, labelleft = False, colors = 'orange')
        self.ax.yaxis.label.set_color('C0')
        self.ax2.yaxis.label.set_color('orange')
        self.ax2.spines['left'].set_color('C0')
        self.ax2.spines['right'].set_color('orange')
    
    # Set up plot to call animate() function periodically
    def animation(self,q):
        self.ani = animation.FuncAnimation(self.fig, self.animate, fargs=(q,), interval=1000) #fargs=(q,),


# ------ Some functions for testing the class ---------------------------------#

def plot_killer(my_plot):
    time.sleep(10)
    my_plot.ani.event_source.stop()
    
def data_gen(q):
    i = 0
    # while True:
    for i in range(10):
        i += 1
        q.put(i)
        time.sleep(1)

def inf_sum(i):
    time.sleep(1)
    return i+1    