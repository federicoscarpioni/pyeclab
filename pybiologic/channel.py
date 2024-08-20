import numpy as np
from collections import namedtuple
from threading import Thread
import time
import logging
from device import BiologicDevice
from auxiliary_functions import save_exp_metadata, create_data_file_for_saving, SavingMetadata, get_saving_path, write_latest_data_to_file
from api.tech_types import TECH_ID

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)

ChannelOptions = namedtuple('ChannelOptions', ['measurement_name'])

class Channel:
    
    def __init__(self,
                 bio_device : BiologicDevice, 
                 channel_num : int, 
                 saving_path : str,
                 channel_options : namedtuple,
                 record_Ece : bool = False,
                 record_analog_in1 : bool = False,
                 record_analog_in2 : bool = False,
                 logging_level : logging.INFO = logging.WARNING, # !!! I am not sure this type is correct
                 print_values : bool  = False):
        self.bio_device       = bio_device
        self.num              = channel_num
        self.saving_path      = saving_path
        self.measurement_name = channel_options.measurement_name # !!! maybe I can save directly the whole options
        self.print_values     = print_values
        

    # Methods for setting hardware and commands

    def set_hardware_config(self):
        ...

    def load_sequence(self, sequence): 
        self.sequence = sequence
        self.bio_device.load_sequence(self.num, self.sequence) 

    def start(self): 
        self.saving_file_handle = _create_saving_file()
        save_exp_metadata()
        self.bio_device.start_channel(self.num)  
        loop_thread = Thread(target=self.data_transfer_loop)
        loop_thread.start()
        print(f'CH{self.num}: Experiment started')

    def stop(self):
        self.bio_device.stop_channel(self.num)
        self._close_saving_file()
        print(f'CH{self.num}: interrupted by the user')  
    

    # Methods for managing the main loop

    def _retrive_data_loop(self, sleep_time = 0.1):
        '''
        Retrives latest measurement data from the BioLogic device, converts and 
        saves. The sequence progression is also monitored.
        '''
        while True:
            # Get data from instrument ADC
            self._get_data()
            # Convert ADC numbers to physical values
            latest_data = self._convert_buffer_to_physical_values(self.data_buffer)
            # Write on open file
            self._write_latest_data_to_file(latest_data)
            # Print latest values 
            if self.print_values : self._print_current_values()
            # Check if the technique has changed on the instrument
            self._monitoring_sequnce_progression()
            # Brake the loop if sequence is terminates
            if self.current_values.Status == 0:
                self._close_saving_file()
                print(f'CH{self.num}: Sequence terminated')
                break
            # Sleep before retriving next measrued data
            time.sleep(sleep_time)

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

    def _monitoring_sequnce_progression(self):
        '''
        This methods checks when a new technique is started in the instrument. This
        can be used to add new beahviours to the application.
        '''
        new_tech_index = self.data_info.TechniqueIndex
        new_tech_id    = self.data_info.TechniqueID
        if self.is_running == False:
            self.current_tech_index = new_tech_index
            self.current_tech_id    = new_tech_id
            self.is_running = True
        # Check if a new technique is running
        if self.current_tech_index != new_tech_index : 
            if self.debug: print(f'> CH{self.num} msg: new technique ongoing detected by the software')

    def _print_current_values(self):
        print(f'CH{self.num} - Ewe: {self.current_values.Ewe:.4}V | I: {self.current_values.I*1000:.4}mA | Tech_ID: {TECH_ID(self.current_values.TechniqueID).name} | Tech_indx: {self.current_values.TechniqueIndex} | loop: {self.current_values.loop}')
               
    def _convert_buffer_to_physical_values(self): # Maybe it is not necessary to make buffers attributes
        '''
        Convert digitalized signal from ADC to physical values.

        Note: Counter electrode  and AUX to be added!    

        '''
        # Buffer from the device
        buffer = np.array(self.data_buffer).reshape(self.data_info.NbRows, self.data_info.NbCols)
        # Convert voltage buffer numbers in real values
        Ewe = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i,2]) for i in range(0, self.data_info.NbRows)])
        # Convert buffer numbers in real values, I is 0 for OCV (ID 100)
        if self.data_info.TechniqueID != 100:
            I = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i,3]) for i in range(0, self.data_info.NbRows)]) 
        else:
            I = np.array([0]*len(self.Ewe))
        # Convert time in seconds
        t = np.array([(((buffer[i,0] << 32) + buffer[i,1]) * self.current_values.TimeBase) + self.data_info.StartTime for i in range(0, self.data_info.NbRows)])
        return t, Ewe, I # !!! I think is better to output a named tuple

    # Methods for saving    

    def _create_saving_file(self):
        file_name = self.saving_path + self.measurement_name
        self.saving_file = open(file_name, 'w+') 
        # Write headers
        self.saving_file.write('Time/s\tVoltage/V\tCurrent/A\tTechnique_num\tLoop_num') #!!! Include the possibility to add Ece and Aux

    def _write_latest_data_to_file(self, data):
        technique_num = self.current_tech_index * np.ones(len(data[0]))
        loop_num = self.data_info.loop * np.ones(len(data[0]))
        # Concatenate measurement values and technique data. The use of if statment
        # allows to include also the case of recorder Ece and Auxiliary input
        for i in len(data):
            data_to_save = np.concatenate((data[i]), axis=1)
        data_to_save = np.concatenate((data_to_save, technique_num, loop_num), axis =1) 
        # Write data to saving_file
        data_to_save.tofile(self.saving_file, sep= '\t', format = '%4.3e')

    def _close_saving_file(self):
        self.saving_file.close()

    
    # ---- Methods to be reviewed ---- #

    def save_exp_params(self):
        savepath = f'{self.experiment_info.deis_directory}/{self.experiment_info.project_name}/{self.experiment_info.cell_name}/{self.experiment_info.experiment_name}CH{self.num}/'
        # Create the path
        Path(savepath).mkdir(parents=True, exist_ok=True)
        with open(savepath+'exp_details.txt', 'w') as f:
            f.write('Experimental parameters\n\n')
            f.write('Starting time:' + datetime.now().strftime("%m/%d/%Y-%H:%M:%S"))
            f.write('\n')
            if self.pico is not None:
                f.write('Acquisition with Picoscope\nSampling starting time:'+self.pico.time_start.strftime("%m/%d/%Y-%H:%M:%S")+'\n')
            for key, value in self.experiment_info.__dict__.items(): 
                f.write('%s: %s\n' % (key, value))
            f.write('\nSoftware paramteres\n')
            for key, value in self.software_params.__dict__.items(): 
                f.write('%s: %s\n' % (key, value))
            f.write('\nSequence paramters\n')
            for i in range(0,len(self.sequence)):
                f.write(f'\nTechnique #{i}: ' + self.sequence[i].ecc_file[:-5])
                f.write('\n')
                for key, value in self.sequence[i].user_params.__dict__.items(): 
                    f.write('%s: %s\n' % (key, value))  

    def copy_buffer(self):
        ''' 
        Copy converted data buffers to an allocated array. next_sample variable
        contains the first 'free' (or empty, i.e. zero element) index to start 
        the copy from.
        '''
        dest_end = self.next_sample + self.Ewe_buff.size
        if dest_end > self.max_array_allocation:
            self.save_data(True)
            self.inizialize_arrays()
            dest_end = self.Ewe_buff.size
        if self.pico is not None and self.pico.nextSample > self.max_array_allocation:
            self.save_data(True)
            dest_end = self.Ewe_buff.size
        self.Ewe[self.next_sample:dest_end]             = self.Ewe_buff
        self.I[self.next_sample:dest_end]               = self.I_buff
        self.time_experiment[self.next_sample:dest_end] = self.t_buff
        self.next_sample = dest_end
        self.send_data_to_queue(self.downsampling_factor) # !!! soft code the downsampling constant
 
    def end_technique(self):
        ''' 
        End the current technique in the sequence by replacing its original
        duration to the value of 1 second (This is a workaround for the lack
        of a specific function in the BioLogic library). At the end the original
        duration is reset for the successive cycle. 
        The data for the current technique are saved and the array re-allocated.
        '''
        self.bio_device.UpdateParameters(self.bio_device.device_id,
                                         self.num,
                                         self.current_tech_index,
                                         bt.duration_to_1s(self.bio_device, self.sequence[self.current_tech_index], self.current_tech_id),
                                         self.sequence[self.current_tech_index].ecc_file)
        
        self.bio_device.UpdateParameters(self.bio_device.device_id,
                                         self.num,
                                         self.current_tech_index,
                                         bt.reset_duration(self.bio_device, self.sequence[self.current_tech_index], self.current_tech_id),
                                         self.sequence[self.current_tech_index].ecc_file)

    def get_technique_name(self):
        if self.current_tech_id == 100:
            technique_name = 'OCV'
        elif self.current_tech_id == 101:
            technique_name = 'chonoamperometry'
        elif self.current_tech_id == 155:
            technique_name = 'chronopotentiometry'
        return technique_name

    def update_potentiostatic_value(self, Ewe, new_tech_index):
        self.bio_device.UpdateParameters(self.bio_device.device_id,
                                         self.num,
                                         self.current_tech_index,
                                         bt.update_CA_voltage(self.bio_device, Ewe, self.sequence[new_tech_index]),
                                         self.sequence[new_tech_index].ecc_file)
            
    
    
        
        
        
    

        
    
    
    
    
    