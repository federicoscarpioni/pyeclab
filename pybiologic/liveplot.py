import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.animation as animation
import numpy as np
import time


class LivePlot():

    def __init__(self, 
                channel: Channel, 
                update_interval : int = 1000, # Value in ms
                ):
        self.channel = channel
        self.update_interval = update_interval
        # Pointer for reading the saving file of the channel class. One is used 
        # to skip the header.
        self.last_position = 1  
        self._initialize_figure()
        self._animate()
        
         

    def _initialize_figure(self):
        # Create the figure    
        self.fig, axis = plt.subplots(2)
        self.ax = axis[0]
        self.ax2 = axis[1]
        self.line,  = self.ax.plot ([], [], '-', label = 'Voltage', color='C0')
        self.line2, = self.ax2.plot([], [], '-', label = 'Current', color='orange')
        # Plot styling options
        self.ax.relim()
        self.ax2.relim()
        self.ax.autoscale_view()
        self.ax2.autoscale_view()
        self.ax.set_title(f'Channel {channel.num}')
        self.ax.set_ylabel('Potential (V) / V', color='C0', fontsize=16)
        self.ax2.set_ylabel('Current (A) / mA', color='orange', fontsize=16)
        self.ax.tick_params(axis = 'x', which = 'both', top = False)
        self.ax.tick_params(axis = 'y', which = 'both', right = False, colors = 'C0')
        self.ax2.tick_params(axis = 'y', which = 'both', right = True, labelright = True, left = False, labelleft = False, colors = 'orange')
        self.ax.yaxis.label.set_color('C0')
        self.ax2.yaxis.label.set_color('orange')


    def _read_latest_values(self):
        # Move the cursor on the file
        self.channel.saving_file.seek(self.last_position)
        # Read the new lines
        new_lines = self.channel.saving_file.readlines()
        # Update the cursor
        self.last_position = self.channel.saving_file.tell()
        return new_lines


    # This function is called periodically from FuncAnimation
    def _update_plot(self, i, q):
        # Read new data
        new_lines = self._read_latest_values()
        if new_lines:
            new_data = pd.read_csv(pd.compat.StringIO(''.join(new_lines)), header=None)
            time_data = list(line.get_xdata()) + new_data[0].tolist()
            Ewe_data = list(line.get_ydata()) + new_data[1].tolist()
            I_data = list(line2.get_ydata()) + new_data[2].tolist()

            # Plot the new data
            # After 90 minutes plot in hours
            if self.time[-1]>5400:
                self.line.set_data(time_data/3600, Ewe_data)
                self.line2.set_data(time_data/3600, I_data/1000)
                self.ax.set_xlabel('Time / hour', fontsize=16)
            # After 120 second plot in minutes
            elif self.time[-1]>120: 
                self.line.set_data(time_data/60, Ewe_data)
                self.line2.set_data(time_data/60, I_data/1000)
                self.ax.set_xlabel('Time / min', fontsize=16)
            # Plot in seconds
            else:
                self.line.set_data (time_data, Ewe_data)
                self.line2.set_data(time_data, I_data/1000)
                self.ax.set_xlabel('Time / sec', fontsize=16)
        
        
    
    # Set up plot to call animate() function periodically
    def _animate(self,q):
        self.ani = animation.FuncAnimation(self.fig, self._update_plot, fargs=(q,), interval=self.update_interval)