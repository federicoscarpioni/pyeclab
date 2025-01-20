import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv
import numpy as np
import pandas as pd

# NOTE last point is not plotted


class LivePlot:
    def __init__(
        self,
        channel,
        update_interval: int = 1000,  # Value in ms
    ):
        self.channel = channel
        self.update_interval = update_interval
        # Pointer for reading from the saving file of the channel class. One is used
        # to skip the header.
        self.lines_red = 1
        # self.data_to_plot = []

        # Move the cursor after the firt line that contains the header
        # self.channel.saving_file.readline()
        # self.last_position = self.channel.saving_file.tell()
        self.to_minutes = False
        self.to_hours = False

        # Create the figure
        self.fig, (self.ax, self.ax2) = plt.subplots(2)
        self._initialize_figure()
        self._animate()
        plt.show()

    def _initialize_figure(self):
        # self.ax = axis[0]
        # self.ax2 = axis[1]
        (self.line,) = self.ax.plot([], [], "-", label="Voltage", color="C0")
        (self.line2,) = self.ax2.plot([], [], "-", label="Current", color="orange")
        # Plot styling options
        self.ax.relim()
        self.ax2.relim()
        self.ax.autoscale_view()
        self.ax2.autoscale_view()
        self.ax.set_title(f"Channel {self.channel.num}")
        self.ax.set_ylabel("Potential / V", color="C0", fontsize=14)
        self.ax2.set_ylabel("Current / mA", color="orange", fontsize=14)
        self.ax.grid(True)
        self.ax2.grid(True)

    def _read_latest_values(self):
        if not self.channel.saving_file.closed:
            # == Read and split approach ==
            # # Move the cursor on the file
            # self.channel.saving_file.seek(self.last_position)
            # # Read the new lines
            # new_lines = self.channel.saving_file.read()
            # # Split the data into rows (lines) and then into columns (by tabs)
            # rows = [line.split('\t') for line in new_lines.strip().split('\n') if line]
            # print(rows)
            # #Convert the list of rows into a NumPy array
            # array = np.array(rows, dtype=float)
            # # Update the cursor to last position
            # self.last_position = self.channel.saving_file.tell()

            # == Pandas approach ==
            new_lines = pd.read_csv(
                self.channel.saving_path + "/measurement_data.txt", delimiter="\t", skiprows=self.lines_red
            )
            self.lines_red = self.lines_red + len(new_lines.index)

            # == tofile approach ==
            # new_lines = np.fromfile(self.channel.saving_path, sep = '\t') # Fails: numpy as no permissions

            # == loadtxt approadh ==
            # new_data = np.loadtxt(self.channel.saving_file, dtype='float', delimiter='\t', skiprows=self.last_position)
            # self.last_position=self.last_position+new_data.shape[0]

            return new_lines

    # This function is called periodically from FuncAnimation
    def _update_plot(self, frame):
        # Read new data
        # self.data_to_plot.append(self._read_latest_values())
        new_data = self._read_latest_values()

        # new_data = pd.read_csv(pd.compat.StringIO(''.join(new_lines)), header=None)
        # if type(new_data) != type(None):

        # self.line.set_data(new_data[:,0], new_data[:,1])
        # self.line2.set_data(new_data[:,0], new_data[:,2])

        # self.line.set_data(self.data_to_plot.iloc[:,0], self.data_to_plot.iloc[:,1])
        # self.line2.set_data(self.data_to_plot.iloc[:,0], self.data_to_plot.iloc[:,2])
        if type(new_data) != type(None) and not new_data.empty:
            time_data = np.append(self.line.get_xdata(), new_data.iloc[:, 0])
            Ewe_data = np.append(self.line.get_ydata(), new_data.iloc[:, 1])
            I_data = np.append(self.line2.get_ydata(), new_data.iloc[:, 2] * 1000)
            # Plot the new data
            # # After 90 minutes plot in hours
            # if time_data[-1]>5400:
            #     self.line.set_data(time_data/3600, Ewe_data)
            #     self.line2.set_data(time_data/3600, I_data)
            #     self.ax2.set_xlabel('Time / hour', fontsize=12)
            # # After 120 second plot in minutes
            # elif time_data[-1]>120:
            #     self.line.set_data(time_data/60, Ewe_data)
            #     self.line2.set_data(time_data/60, I_data)
            #     self.ax2.set_xlabel('Time / min', fontsize=12)
            # Plot in seconds
            # else:
            self.line.set_data(time_data, Ewe_data)
            self.line2.set_data(time_data, I_data)
            self.ax2.set_xlabel("Time / sec", fontsize=12)

            self.ax.relim()
            self.ax2.relim()
            self.ax.autoscale_view()
            self.ax2.autoscale_view()
        if self.channel.current_values.State == 0:
            # Stop the animation if the channel is not active
            self.ani.event_source.stop()

    # Set up plot to call animate() function periodically
    def _animate(self):
        self.ani = animation.FuncAnimation(
            self.fig,
            self._update_plot,
            init_func=self._initialize_figure(),
            interval=self.update_interval,
        )
