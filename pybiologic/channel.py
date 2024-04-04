import numpy as np
from threading import Thread
import time
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger(__name__)


def save_exp_metadata(path, metadata):
    '''
    Save all the information regarding the experiment
    '''
    ...

class Channel:
    
    def __init__(self,
                 bio_device, 
                 channel_num, 
                 saving_metadata, 
                 logging_level=logging.WARNING,
                 #verbosity=1,
                 #debug=True
                 ):
        
        self.bio_device   = bio_device
        self.saving_metadata = saving_metadata
        self.num          = channel_num
        self.cycle_number = 1
        self.part_count = 1

    def load_sequence(self, sequence): # change this variables name that are confusing!!
        '''
        Load the sequence of techniques to the instrument channel. 
        '''
        self.sequence = sequence 
        self.bio_device.load_sequence(self.num, self.sequence)         
    
    def measure_loop(self):
        '''
        Main experiment loop, retrives data with a certain frequency from the 
        BioLogic device. Useful to execute the acquisition in a separate thread.
        '''
        while True:
           self.get_data()
           if self.is_running == False:
               break
           time.sleep(.01)

           

    def start(self): 
        save_exp_metadata()
        self.bio_device.start_channel(self.num)
        
        
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
                    
    
        
        
    
        
        

        
        
 
    def convert_buffer(self, data): # Maybe it is not necessary to make buffers attributes
        '''
        Convert BioLogic buffer numbers to physical values.
        '''
        # Buffer from the device
        buff = np.array(data[2]).reshape(data[1].NbRows, data[1].NbCols)
        # Convert voltage buffer numbers in real values
        self.Ewe_buff = np.array([self.bio_device.ConvertNumericIntoSingle(buff[i,2]) for i in range(0,data[1].NbRows)])
        # Convert buffer numbers in real values
        if data[1].TechniqueID != 100:
            self.I_buff = np.array([self.bio_device.ConvertNumericIntoSingle(buff[i,3]) for i in range(0,data[1].NbRows)]) 
        else:
            self.I_buff = np.array([0]*len(self.Ewe_buff))
        # Convert time in seconds
        self.t_buff = np.array([(((buff[i,0] << 32) + buff[i,1]) * data[0].TimeBase) + data[1].StartTime for i in range(0,data[1].NbRows)])
        
    

    
    
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
            
    
    def get_data(self):
        ''' 
        Retrive buffer from instrument memory, convert to physical values and 
        copy into the preallocated arrays. 
        '''
        data = self.bio_device.GetData(self.bio_device.device_id, self.num)
        if self.verbosity>1: print(f'CH{self.num} - Ewe: {data[0].Ewe:.4}V | I: {data[0].I*1000:.4}mA | Tech_ID: {data[1].TechniqueID} | Tech_indx: {data[1].TechniqueIndex} | loop: {data[1].loop}')
        new_tech_index = data[1].TechniqueIndex
        new_tech_id    = data[1].TechniqueID

        # self.update_potentiostatic_value(data[0].Ewe, 4)
        if self.is_running == False:
            self.current_tech_index = new_tech_index
            self.current_tech_id    = new_tech_id
            self.is_running = True
        # Check if a new technique is running
        if self.current_tech_index != new_tech_index : 
            if self.debug: print(f'> CH{self.num} msg: new technique ongoing detected by the software')
            # Save data
            self.save_data()    
            print(f'> CH{self.num} msg > Data saved')
            # Re-initilize technique parameters and flag variables
            self.current_tech_index = new_tech_index
            self.current_tech_id    = new_tech_id
            self.part_count = 1
            if self.verbosity>0: print(f"> Channel {self.num} msg: {self.get_technique_name()} started")

        # Check for sequence end
        if data[0].State == 0 and self.current_tech_id != 0:
            self.save_data()
            if self.verbosity>0: print(f'> CH{self.num} msg: sequence completed from the instrument')
            self.is_running = False
        self.convert_buffer(data) 
        self.copy_buffer()
        
        
        
    def stop(self):
        ''' 
        Stop the experiment execution in the channel.
        '''
        self.bio_device.stop_channel(self.num)
        self.is_running = False

        
    
    
    
    
    