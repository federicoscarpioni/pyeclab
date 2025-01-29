import numpy as np
import json
from datetime import datetime
from pathlib import Path
from collections import namedtuple, deque
from threading import Thread
from np_rw_buffer import RingBuffer
import time
from pyeclab.device import BiologicDevice
import pyeclab.techniques
from pyeclab.techniques import set_duration_to_1s, reset_duration
from pyeclab.api.tech_types import TECH_ID
from pyeclab.liveplot import LivePlot

# ! Add a logger

''' 
!!! Works only for dt of 1 second of the potentiostat. The problem is how to 
!!! save correctly a matrix of values instead of an array
'''

ChannelOptions = namedtuple('ChannelOptions', ['experiment_name'])

# class HardwareConfigManger:
#     def set_hardware_config(self, ...):
#         ...

#     def generate_xctr_param(self, ...):
#         ...

# class ExperimentManager:
#     def start(self, ...):
#         ...

#     def stop(self, ...):
#         ...

# class DataManager:
#     def __init__(self, saving_dir):
#         self.saving_dir = saving_dir

#     def create_exp_folder(self, ...):
#         ...

#     def write_data_to_file(self, ...):
#         ...

# class ConditionChecker:
#     def set_condition(self, ...):
#         ...

#     def check_limits(self, ...):
#         ...

class Channel:
    
    # New to implement:
    # def __init__(self, bio_device, channel_num, saving_dir, channel_options,
    #              hardware_manager, experiment_manager, data_manager, condition_checker):
    #     self.bio_device = bio_device
    #     self.num = channel_num
    #     self.hardware_manager = hardware_manager
    #     self.experiment_manager = experiment_manager
    #     self.data_manager = data_manager
    #     self.condition_checker = condition_checker
    #     ...

    def __init__(self,
                 bio_device : BiologicDevice, 
                 channel_num : int, 
                 saving_dir : str,
                 channel_options : namedtuple,
                 is_live_plotting : bool = True, # ? Deside which naming convention to use for booleans
                 is_recording_Ece : bool = False,
                 is_external_controlled : bool = False,
                 is_recording_analog_In1 : bool = False,
                 is_recording_analog_In2 : bool = False,
                 is_charge_recorded: bool = False,
                 is_printing_values : bool  = False,
                 callbacks = []):
        self.bio_device              = bio_device
        self.num                     = channel_num
        # Saving details
        self.experiment_name         = channel_options.experiment_name # ? maybe I can save directly the whole options
        self.saving_path             = saving_dir + '/' + self.experiment_name
        # Class behaviour
        self.print_values            = is_printing_values
        self.is_live_plotting        = is_live_plotting
        self.callbacks               = callbacks
        self.current_tech_index      = 0
        self.current_loop            = 0
        # Hardware setting
        self.conditions              = []
        self.conditions_average      = []
        self.is_running              = False
        self.is_recording_Ece        = is_recording_Ece
        self.is_external_controlled  = is_external_controlled
        self.is_recording_analog_In1 = is_recording_analog_In1
        self.is_recording_analog_In2 = is_recording_analog_In2
        self.is_charge_recorded      = is_charge_recorded
        self.xtr_param               = self.generate_xctr_param() # This parameter is valid only for premium potentiostat



    ## Methods for setting hardware for the experiment ##

    def set_hardware_config(self):
        ...

    def generate_xctr_param(self):
        bitfield = 0
        bitfield |= self.is_recording_Ece << 0  # Record Ece at bit position 1
        bitfield |= self.is_recording_analog_In1 << 1  # Record Analog IN1 at bit position 2
        bitfield |= self.is_recording_analog_In2 << 2  # Record Analog IN2 at bit position 3
        bitfield |= self.is_external_controlled << 3  # Enable External ctrl at bit position 4
        # bit 5 is reserved
        # No information for bit position 6 (Record Control), assuming not needed
        bitfield |= self.is_charge_recorded << 6  # Record Charge at bit position 7
        # No information for bit position 8 (Record IRange), assuming not needed
        return bitfield

    def load_sequence(self, sequence, ask_ok = False): 
        self.sequence = sequence
        self.bio_device.load_sequence(self.num, self.sequence, display=ask_ok) 
            
            

    def import_sequence(self, json_file_path): 
        with open('json_file_path', 'r') as sequence_json:
            self.sequence = json.load(sequence_json)
        self.bio_device.load_sequence(self.num, self.sequence)


    ## Methods for managing the execution of the experiment ##

    def start(self): 
        # Save experiment data
        self._create_exp_folder()
        self._create_saving_file()
        self._save_exp_metadata()
        # self._save_sequence_json()
        # Start channel on the device
        self.bio_device.start_channel(self.num)  
        # Start collecting data from the device
        loop_thread = Thread(target=self._retrive_data_loop)
        loop_thread.start()
        # Initialize liveplot
        if self.is_live_plotting: self.start_live_plot()
        print(f'CH{self.num}: Experiment started')
        

    def stop(self):
        self.bio_device.stop_channel(self.num)
        self._get_measurement_values() # ? There shoudl be still the latest values to retrive
        print(f'CH{self.num}: interrupted by the user')  

    def start_live_plot(self):
        self.liveplot = LivePlot(self)

    def end_technique(self):
        ''' 
        End the current technique in the sequence by replacing its original
        duration to the value of 1 second (This is a workaround for the lack
        of a specific function in the EC-Lab SDK). 
        '''
        self.bio_device.UpdateParameters(self.bio_device.device_id,
                                        self.num,
                                        self.current_tech_index,
                                        set_duration_to_1s(self.bio_device, self.sequence[self.current_tech_index], self.current_tech_id),
                                        self.sequence[self.current_tech_index].ecc_file)
        
        self.bio_device.UpdateParameters(self.bio_device.device_id,
                                        self.num,
                                        self.current_tech_index,
                                        reset_duration(self.bio_device, self.sequence[self.current_tech_index], self.current_tech_id),
                                        self.sequence[self.current_tech_index].ecc_file)
    
    def _print_current_values(self):
        print(f"CH{self.num} > Ewe: {self.current_values.Ewe:4.3e} V | I: {self.current_values.I:4.3e} mA | Tech_ID: {TECH_ID(self.data_info.TechniqueID).name} | Tech_indx: {self.data_info.TechniqueIndex} | loop: {self.data_info.loop}")
    

    ## Methods for managing data collaction in the main loop ##

    def _final_actions(self):
        '''
        Operations to perfom when the sequence is completed.
        '''
        self._close_saving_file()
        self._execute_callbacks()
        print(f'CH{self.num} > Measure terminated')
    
    def _retrive_data_loop(self, sleep_time = 0.1):
        '''
        Retrives latest measurement data from the BioLogic device, converts and 
        saves. The sequence progression is also monitored.
        '''
        while True:
            self.latest_data = self._get_measurement_values()
            # Write latest data to open saving file
            self._write_latest_data_to_file()
            # Print latest values 
            if self.print_values : self._print_current_values()
            # Update plot
            # self.liveplot.update_plot()
            # Check if the technique has changed on the instrument
            self._monitoring_sequence_progression()
            # Brake the loop if sequence is terminates
            if self.current_values.State == 0:
                self._final_actions()
                break
            # Stop current technique if any software limit is reached
            if self._check_software_limits():
                print('Software limits met') # debug print
                self.end_technique()
            if self._check_software_limits_avarage():
                print('Software limits avarage met') # debug print
                self.end_technique()    
            # Sleep before retriving next measrued data
            time.sleep(sleep_time)

    def _get_measurement_values(self):
        # Get data from instrument ADC
        self._get_data()
        # Convert ADC numbers to physical values
        latest_data = self._get_converted_buffer()
        return latest_data

    def _get_data(self):
        ''' 
        When retriving latest agglomerated data from the instrument, the api will
        return three objects: 
        current_values = current values of the measurement
        data_info = info on  the technique that is running and on the buffer content
        data_buffer = data in a one dimension
        See the EC-Lab Development Kit manual for details on the data structures.
        '''
        self.current_values, self.data_info, self.data_buffer = self.bio_device.GetData(self.bio_device.device_id, self.num)

    def _get_converted_buffer_base(self, buffer):
        Ewe = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 2]) for i in range(0, self.data_info.NbRows)])
        I = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 3]) for i in range(0, self.data_info.NbRows)]) if self.data_info.TechniqueID != 100 else np.array([0] * len(Ewe))
        t = np.array([(((buffer[i, 0] << 32) + buffer[i, 1]) * self.current_values.TimeBase) + self.data_info.StartTime for i in range(0, self.data_info.NbRows)])
        return t, Ewe, I

    def _get_converted_buffer_with_charge(self, buffer):
        t, Ewe, I = self._get_converted_buffer_base(buffer)
        q = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, self.data_info.NbRows)])
        return t, Ewe, I, q

    def _get_converted_buffer_with_Ece(self, buffer):
        t, Ewe, I = self._get_converted_buffer_base(buffer)
        Ece = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, self.data_info.NbRows)])
        return t, Ewe, I, Ece

    def _get_converted_buffer_with_charge_and_Ece(self, buffer):
        t, Ewe, I = self._get_converted_buffer_base(buffer)
        Ece = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, self.data_info.NbRows)])
        q = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 6]) for i in range(0, self.data_info.NbRows)])
        return t, Ewe, I, Ece, q

    def _get_converted_buffer(self):
        '''
        Convert digitalized signal from ADC to physical values.

        Note: Counter electrode  and AUX to be added!    

        '''
        # Buffer from the device
        buffer = np.array(self.data_buffer).reshape(self.data_info.NbRows, self.data_info.NbCols)
        # Convert voltage buffer numbers in real values
        Ewe = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i,2]) for i in range(0, self.data_info.NbRows)])
        # Convert buffer numbers in real values
        if self.is_charge_recorded and self.is_recording_Ece:
            return self._get_converted_buffer_with_charge_and_Ece(buffer)
        elif self.is_charge_recorded:
            return self._get_converted_buffer_with_charge(buffer)
        elif self.is_recording_Ece:
            return self._get_converted_buffer_with_Ece(buffer)
        else:
            return self._get_converted_buffer_base(buffer)
        
    
    def _execute_callbacks(self):
        for callback in self.callbacks:
            if callable(callback):
                callback()
    
    def _update_sequence_trackers(self):
        self.current_tech_index = self.data_info.TechniqueIndex
        self.current_tech_id    = self.data_info.TechniqueID
        self.current_loop       = self.data_info.loop
        
    
    def _monitoring_sequence_progression(self):
        '''
        This method checks when a new technique is started in the instrument. This
        can be used to add new behaviours to the application.
        '''
        new_tech_index = self.data_info.TechniqueIndex
        new_tech_id    = self.data_info.TechniqueID
        new_loop       = self.data_info.loop
        if not self.is_running:
            self.is_running = True
            self.current_tech_id = new_tech_id
        # Check if a new technique is running
        if self.current_loop != new_loop or self.current_tech_index != new_tech_index : # the second condition should be sufficient...
            self._update_sequence_trackers()
            self._execute_callbacks()
            print(f'> CH{self.num} msg: new technique started ({self.data_info.TechniqueID})')



    ## Methods for software controll ##          
    
    def set_condition(self, technique_index: int, quantity:str, operator:str, threshold:float):
        self.conditions.append((technique_index,quantity, operator, threshold))
    
    def _check_software_limits(self):
        '''
        Check if a certain condition (< or > of a trashold value) is met for a 
        value of the sampled data over a certain number of points.
        '''
        for technique_index, quantity, operator, threshold in self.conditions:              # ? Can I manually add other attributes to current_values for the quantities that are missing?
            if self.data_info.TechniqueIndex == technique_index:    
                quantity_value = getattr(self.current_values, quantity, None) # ! It works only for attributes of current_data. I need onther trick to make it work also for capacity or power
                if quantity_value is None:
                    continue
                if operator == '>' and quantity_value >= threshold:
                    print(f'{quantity} > {quantity_value} in technique {technique_index}')
                    return True
                elif operator == '<' and quantity_value <= threshold:
                    print(f'{quantity} < {quantity_value} in technique {technique_index}')
                    return True
        return False # Do I need to keep this return?
    

    def set_condition_avarage(self, technique_index: int, quantity:str, operator:str, threshold:float, points_avarage:int):
        '''
        latest_points is a circular buffer. It is saved in the condition tuple.
        '''
        latest_points = RingBuffer(points_avarage)
        self.conditions_average.append((technique_index, quantity, operator, threshold,points_avarage, latest_points))

    def _update_value_buffer(self, buffer, data):
        buffer.write(data, error = False)
        return buffer
    
    def _reset_buffer_avarage(self):
        for technique_index, quantity, operator, threshold, points_avarage, latest_points in self.conditions_average:
            latest_points.read()

    def _get_avarage(self, buffer):
        return np.sum(buffer.get_data())/len(buffer.get_data())
        
    def _check_software_limits_avarage(self):
        '''
        Check if a certain condition (< or > of a trashold value) is met for the
        avarage value of a sampled data over a certain number of points.
        '''
        for technique_index, quantity, operator, threshold, points_avarage, latest_points in self.conditions_average:   # ? Can I manually add other attributes to current_values for the quantities that are missing?
            quantity_value = getattr(self.current_values, quantity, None) # ! It works only for attributes of current_data. I need onther trick to make it work also for capacity or power
            if self.current_tech_index != technique_index:
                continue
            if quantity_value is None:
                continue
            latest_points = self._update_value_buffer(latest_points, quantity_value)
            if len(latest_points)<points_avarage:
                continue
            avarage_value = self._get_avarage(latest_points)
            if operator == '>' and avarage_value >= threshold:
                print(f'{quantity} > {avarage_value} in technique {technique_index}')
                self._reset_buffer_avarage()
                return True
            elif operator == '<' and avarage_value <= threshold:
                print(f'{quantity} < {avarage_value} in technique {technique_index}')
                self._reset_buffer_avarage()
                return True
        return False
           


    ## Methods for saving data ##   

    def _create_exp_folder(self):
        Path(self.saving_path).mkdir(parents=True, exist_ok=True)

    def _create_saving_file(self):       
        self.saving_file = open(self.saving_path + '/measurement_data.txt', 'w+') 
        # Write headers
        if self.is_recording_Ece and self.is_charge_recorded:
            self.saving_file.write('Time/s\tEwe/V\tI/A\tEce/V\tQ/C\tTechnique_num\tLoop_num\n')
        elif self.is_recording_Ece:
            self.saving_file.write('Time/s\tEwe/V\tI/A\tEce/V\tTechnique_num\tLoop_num\n')
        elif self.is_charge_recorded:
            self.saving_file.write('Time/s\tEwe/V\tI/A\tQ/C\tTechnique_num\tLoop_num\n')
        else:
            self.saving_file.write('Time/s\tEwe/V\tI/A\tTechnique_num\tLoop_num\n')

    def _write_latest_data_to_file(self):
        technique_num = self.current_tech_index * np.ones(len(self.latest_data[0]))
        loop_num = self.data_info.loop * np.ones(len(self.latest_data[0]))

        # !!! This block of logic statement is horrible, there must be a better solution! Also, this is not including Auxiliary In record
        if self.is_recording_Ece and self.is_charge_recorded:
            data_to_save = np.column_stack((self.latest_data[0],
                                            self.latest_data[1],
                                            self.latest_data[2],
                                            self.latest_data[3],
                                            self.latest_data[4],
                                            technique_num,
                                            loop_num))
        elif self.is_recording_Ece:
            data_to_save = np.column_stack((self.latest_data[0],
                                            self.latest_data[1],
                                            self.latest_data[2],
                                            self.latest_data[3],
                                            technique_num,
                                            loop_num))
        elif self.is_charge_recorded:
            data_to_save = np.column_stack((self.latest_data[0],
                                            self.latest_data[1],
                                            self.latest_data[2],
                                            self.latest_data[3],
                                            technique_num,
                                            loop_num))
        else:
            data_to_save = np.column_stack((self.latest_data[0],
                                            self.latest_data[1],
                                            self.latest_data[2],
                                            technique_num,
                                            loop_num))

        np.savetxt(self.saving_file, data_to_save, fmt= '%4.3e', delimiter= '\t')
        self.saving_file.flush()

    def _close_saving_file(self):
        self.saving_file.close()

    def _save_exp_metadata(self):
        # Note: I am not using the 'with' constructor here because I assume I 
        # might want to update the metada if some event happen. In that case,
        # the closing function should be move in the stop() method.
        self.metadata_file = open(self.saving_path + '/experiment_metadata.txt', 'w')
        # File title
        self.metadata_file.write('PYECLAB METADATA FILE\n')
        # Information of the starting time
        self.starting_time = datetime.now()
        self.metadata_file.write(f"Date : {self.starting_time.strftime('%Y-%m-%d')}\n")
        self.metadata_file.write(f"Starting time : {self.starting_time.strftime('%H:%M:%S')}\n")
        # Information of the saving file name
        self.metadata_file.write(f'Experiment name : {self.experiment_name}\n')
        self.metadata_file.write(f'Saving file path : {self.saving_path}\n')
        # !!! Print all the information of the techniques in the sequence
        # ! Add information on the device, channel number, cell name and user comments
        # ! Add the list of condition checked by the software
        self.metadata_file.close()

    def _save_sequence_json(self):
        json_file_path = self.saving_path + '/sequence.json'
        with open(json_file_path, 'w') as json_file:
            json.dump(self.sequence, json_file)

    # ---- Methods to be reviewed ---- #

    # def save_exp_params(self):
    #     savepath = f'{self.experiment_info.deis_directory}/{self.experiment_info.project_name}/{self.experiment_info.cell_name}/{self.experiment_info.experiment_name}CH{self.num}/'
    #     # Create the path
    #     Path(savepath).mkdir(parents=True, exist_ok=True)
    #     with open(savepath+'exp_details.txt', 'w') as f:
    #         f.write('Experimental parameters\n\n')
    #         f.write('Starting time:' + datetime.now().strftime("%m/%d/%Y-%H:%M:%S"))
    #         f.write('\n')
    #         if self.pico is not None:
    #             f.write('Acquisition with Picoscope\nSampling starting time:'+self.pico.time_start.strftime("%m/%d/%Y-%H:%M:%S")+'\n')
    #         for key, value in self.experiment_info.__dict__.items(): 
    #             f.write('%s: %s\n' % (key, value))
    #         f.write('\nSoftware paramteres\n')
    #         for key, value in self.software_params.__dict__.items(): 
    #             f.write('%s: %s\n' % (key, value))
    #         f.write('\nSequence paramters\n')
    #         for i in range(0,len(self.sequence)):
    #             f.write(f'\nTechnique #{i}: ' + self.sequence[i].ecc_file[:-5])
    #             f.write('\n')
    #             for key, value in self.sequence[i].user_params.__dict__.items(): 
    #                 f.write('%s: %s\n' % (key, value))  

    # def copy_buffer(self):
    #     ''' 
    #     Copy converted data buffers to an allocated array. next_sample variable
    #     contains the first 'free' (or empty, i.e. zero element) index to start 
    #     the copy from.
    #     '''
    #     dest_end = self.next_sample + self.Ewe_buff.size
    #     if dest_end > self.max_array_allocation:
    #         self.save_data(True)
    #         self.inizialize_arrays()
    #         dest_end = self.Ewe_buff.size
    #     if self.pico is not None and self.pico.nextSample > self.max_array_allocation:
    #         self.save_data(True)
    #         dest_end = self.Ewe_buff.size
    #     self.Ewe[self.next_sample:dest_end]             = self.Ewe_buff
    #     self.I[self.next_sample:dest_end]               = self.I_buff
    #     self.time_experiment[self.next_sample:dest_end] = self.t_buff
    #     self.next_sample = dest_end
    #     self.send_data_to_queue(self.downsampling_factor) # !!! soft code the downsampling constant
 


    # def get_technique_name(self):
    #     if self.current_tech_id == 100:
    #         technique_name = 'OCV'
    #     elif self.current_tech_id == 101:
    #         technique_name = 'chonoamperometry'
    #     elif self.current_tech_id == 155:
    #         technique_name = 'chronopotentiometry'
    #     return technique_name

    # def update_potentiostatic_value(self, Ewe, new_tech_index):
    #     self.bio_device.UpdateParameters(self.bio_device.device_id,
    #                                      self.num,
    #                                      self.current_tech_index,
    #                                      bt.update_CA_voltage(self.bio_device, Ewe, self.sequence[new_tech_index]),
    #                                      self.sequence[new_tech_index].ecc_file)
            
    
    
        
        
        
    

        
    
    
    
    
    