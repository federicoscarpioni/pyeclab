

#=== Helper functions =========================================================#

def duration_to_1s(api, technique, tech_id):
    new_duration = 1
    parameters={
        'current_step':  ECC_parm("Current_step", float),
        'voltage_step':  ECC_parm("Voltage_step", float),
        'step_duration': ECC_parm("Duration_step", float),
        'vs_init':       ECC_parm("vs_initial", bool),
        }
    idx = 0 # Only one current step is used 
    p_current_steps  = list()
    if tech_id == 155:
       p_current_steps.append( make_ecc_parm(api, parameters['current_step'], technique.user_params.current, idx ) )
    elif tech_id == 101:
       p_current_steps.append( make_ecc_parm(api, parameters['voltage_step'], technique.user_params.voltage, idx ) )
    p_current_steps.append( make_ecc_parm(api, parameters['step_duration'], new_duration, idx ) )
    p_current_steps.append( make_ecc_parm(api, parameters['vs_init'], technique.user_params.vs_init, idx ) )
    return make_ecc_parms(api,*p_current_steps)

#------------------------------------------------------------------------------#

def reset_duration(api, technique, tech_id):
    parameters={
        'current_step':  ECC_parm("Current_step", float),
        'voltage_step':  ECC_parm("Voltage_step", float),
        'step_duration': ECC_parm("Duration_step", float),
        'vs_init':       ECC_parm("vs_initial", bool),}
    idx = 0 # Only one current step is used 
    p_current_steps  = list()
    if tech_id == 155:
       p_current_steps.append( make_ecc_parm(api, parameters['current_step'], technique.user_params.current, idx ) )
    elif tech_id == 101:
       p_current_steps.append( make_ecc_parm(api, parameters['voltage_step'], technique.user_params.voltage, idx ) )
    p_current_steps.append( make_ecc_parm(api, parameters['step_duration'], technique.user_params.duration, idx ) )
    p_current_steps.append( make_ecc_parm(api, parameters['vs_init'], technique.user_params.vs_init, idx ) )
    return make_ecc_parms(api,*p_current_steps)

#------------------------------------------------------------------------------#

def update_CA_voltage(api, Ewe, technique):
    CA_parm_names = {
        'voltage_step':  ECC_parm("Voltage_step", float),
        'step_duration': ECC_parm("Duration_step", float),
        'vs_init':       ECC_parm("vs_initial", bool),
        }
    idx = 0 # Only one current step is used 
    p_voltage_steps  = list()
    p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['voltage_step'], Ewe, idx ) )
    p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['step_duration'], technique.user_params.duration, idx ) )
    p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['vs_init'], technique.user_params.vs_init, idx ) )
    return make_ecc_parms(api,*p_voltage_steps)

#==============================================================================#

class Channel:
    
    def __init__(self, 
                 channel_num, 
                 bio_device, 
                 software_params,
                 experiment_info, 
                 liveplot_time_interval,
                 awg = None, 
                 pico = None,
                 verbosity=1,
                 debug=True):
        
        self.bio_device   = bio_device
        self.num          = channel_num
        self.awg          = awg
        self.pico         = pico
        self.is_running   = False
        self.verbosity    = verbosity
        self.debug        = debug
        self.experiment_info = experiment_info
        self.liveplot_time_interval = liveplot_time_interval
        # if battery cyclation:
        self.is_cycling = True  #!!! do something
        self.software_params = software_params #!!! Redundant??
        self.Ewe_lim_high = software_params.Ewe_lim_high
        self.Ewe_lim_low  = software_params.Ewe_lim_low
        self.ca_I_limit   = software_params.ca_I_limit
        self.cycle_number = 1
        self.part_count = 1
        self.multisine_galvano_ampli  = software_params.multisine_galvano_ampli
        self.multisine_potentio_ampli = software_params.multisine_potentio_ampli
        # for long ciclations
        self.max_array_allocation = software_params.max_array_allocation
        

        
    
    def load_sequence(self, sequence): # change this variables name that are confusing!!
        '''
        Load the sequence of techniques to the instrument channel. 
        '''
        self.sequence = sequence
        self.bio_device.load_sequence(self.num, self.sequence)
        
    
    def choose_allocation_lenght(self, overflow = 0.2): 
        # add if statment if this is technique controlled or time controlled
        
        # Note that the current_tech_id is currently referring to the technique
        # just stopped. It is updated suring the get_data method execution. 
        # status = self.bio_device.GetCurrentValues(self.bio_device.device_id, self.num).State 
        # Choose the proper index of the technique in the sequence
        # if self.is_running :
        index = self.current_tech_index 
        # else:
        #     index = 0
        allocation_length = self.sequence[index].user_params.duration / self.sequence[index].user_params.record_dt
        allocation_length = int(allocation_length + allocation_length*overflow)
        if allocation_length > self.max_array_allocation:
            allocation_length = self.max_array_allocation
        if self.debug: 
            print(f'> CH{self.num}: Allocated array of {allocation_length} elements.')
        return allocation_length
    
    
    def inizialize_arrays(self):
        '''
        Allocate numpy arrays in memory for voltage, current and time. Also the 
        variable next_sample is initialized to use it in the copy_buffer function.
        '''
        allocation_length    = self.choose_allocation_lenght() # !!! remove this hard-coded value
        self.Ewe             = np.zeros(allocation_length, dtype='float32')
        self.I               = np.zeros(allocation_length, dtype='float32')
        self.time_experiment = np.zeros(allocation_length, dtype='float32')
        self.next_sample     = 0 
        
    
    def measure_loop(self):
        '''
        Main experiment loop, retrives data with a certain frequency from the 
        BioLogic device. Useful to execute the acquisition in a separate thread.
        '''
        while True:
           self.get_data()
           # self.liveplot.update(self.Ewe, self.I, self.time_experiment)
           # self.live_plot() !!! TO DO
           if self.is_running == False:
               if self.verbosity>0: print(f'> Channel {self.num} msg: measure terminated')
               self.liveplot.ani.event_source.stop()
               break
           time.sleep(.01)
        # return data_dwnsmpld
           
    def live_plot_loop(self):
        self.liveplot.update(self.Ewe_dwnspld, self.I_dwnspld, self.time_experiment_dwnsmpld)
        time.sleep(1)
        
        
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
                    
    def compute_downsampling_factor(self):
        return int(self.liveplot_time_interval/self.sequence[self.current_tech_index].user_params.record_dt)
        
        
    def start(self): 
        '''
        Start the measure (following loaded sequence of techniques) on the 
        instrument channel and start the data acquisition process in a separate 
        thread.
        '''
        
        # Prepare live plotting
        queue = create_queues()
        self.liveplot = Liveplot(self.num)
        self.current_tech_index = 0
        self.queue_Ewe = queue[0]
        self.queue_I = queue[1]
        self.queue_time = queue[2]
        self.liveplot.animation([self.queue_Ewe, self.queue_I, self.queue_time])
        self.downsampling_factor = self.compute_downsampling_factor()
        # Software paramrters
        self.next_sample = 0
        self.inizialize_arrays() # arrays are initialized  in the first get data
        
        # Start devices
        if self.awg is not None :
            self.awg.turn_on()  # deprecated. It is done in the get_data function when technique is changed
        self.bio_device.start_channel(self.num)
        if self.pico is not None: self.pico.run_streaming_non_blocking()
        measure_loop_thread = Thread(target = self.measure_loop)
        measure_loop_thread.setDaemon(True)
        measure_loop_thread.start()
        
        self.save_exp_params()

        
        
 
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
        
    
    def downsample_datasest(self, data_sdwnsmpld, downsampling_factor):
        # Append to downsampled list
        self.Ewe_dwnspld.append(self.Ewe_buff[::downsampling_factor])
        self.I_dwnspld.append(self.Ewe_buff[::downsampling_factor])
        self.time_experiment_dwnspld.append(self.Ewe_buff[::downsampling_factor])
        return
    
    
    def send_data_to_queue(self, downsampling_factor):
        self.queue_Ewe.put(self.Ewe_buff[::downsampling_factor])
        self.queue_I.put(self.I_buff[::downsampling_factor])
        self.queue_time.put(self.t_buff[::downsampling_factor])
    
    
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

    
    
    def initialize_for_new_technique(self): # write separatly because maybe I want to add other stuff
        self.inizialize_arrays()
        
    
    def software_limits_check(self, data):
        '''
        Stop the current technique (charge or discharge) when the upper or 
        lower voltage limits are read by the acquisition software. In the 
        same time the multisine in the waveform generator is changed accordingly
        to the technique. If the maximum number of cycles is reached the 
        channel is stopped.
        Note: these are software limits monitored by Python process, not the 
        hardware limits controlled by the potentiostat itself.
        '''
        if data[0].Ewe > self.Ewe_lim_high and data[1].TechniqueID == 155 and data[0].I>0:
            self.end_technique()
            if self.verbosity>0: print(f'> Channel {self.num} msg: End constant current charging')
        if data[1].TechniqueID == 101 and data[0].I < self.ca_I_limit: # 101 is ID for CA
            self.end_technique()
            if self.verbosity>0: print(f'> Channel {self.num} msg: End constant potential charging')
        if data[0].Ewe < self.Ewe_lim_low and data[1].TechniqueID == 155 and data[0].I<0:
            self.end_technique()
            # save plot
            # reset liveplot
            if self.verbosity>0: print(f'> Channel {self.num} msg: End discharging')  
    
    
    def get_technique_name(self):
        if self.current_tech_id == 100:
            technique_name = 'OCV'
        elif self.current_tech_id == 101:
            technique_name = 'chonoamperometry'
        elif self.current_tech_id == 155:
            technique_name = 'chronopotentiometry'
        return technique_name
    
    
    def change_waveform(self):
        if self.current_tech_id == 101:
            self.awg.turn_off()
            self.awg.select_awf('ms_ptz')
            self.awg.set_amplitude(self.multisine_potentio_ampli) 
            self.awg.set_offset(0)
            self.awg.turn_on()
        elif self.current_tech_id == 155:
            self.awg.turn_off()
            self.awg.select_awf('ms_glv')
            self.awg.set_amplitude(self.multisine_galvano_ampli) 
            self.awg.set_offset(0)
            self.awg.turn_on()
            
    
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
            self.inizialize_arrays()
            self.part_count = 1
            self.downsampling_factor = self.compute_downsampling_factor()
            if self.awg is not None : self.change_waveform(); print(f'> Waveform changed (tech id {self.current_tech_id})')
            if self.verbosity>0: print(f"> Channel {self.num} msg: {self.get_technique_name()} started")
        # Check for sequence end
        if data[0].State == 0 and self.current_tech_id != 0:
            self.save_data()
            if self.verbosity>0: print(f'> CH{self.num} msg: sequence completed from the instrument')
            self.is_running = False
            if self.awg is not None: self.awg.turn_off()
            if self.pico is not None: self.pico.stop() # I removed this line to try avoid an error, I think now it is not very necessary for the software.
        # if self.current_tech_id == 100: 
            # Update voltage for next technique
        self.convert_buffer(data) 
        self.copy_buffer()
        # self.pico.check_memory_limit(self.max_array_allocation) # TODO! Now is incorporated in copy_buffer
        # self.cycle_number = data[1].loop + 1 # I am moving this to the end of the discharge loop event
        self.software_limits_check(data)
        
        
        
    def stop(self):
        ''' 
        Stop the experiment execution in the channel.
        '''
        self.bio_device.stop_channel(self.num)
        self.is_running = False
        if self.pico is not None: 
            self.pico.stop()
            # self.pico.disconnect() # I removed this for multichannel runs, I have to test the effect
        
    
    
    def save_signal(self, savepath, signal_name, signal):
        np.save(savepath + f'/{signal_name}.npy', signal)
        del(signal)
        
        
        
    def save_pico_signal(self, savepath, signal_name, signal,  vrange, irange):
        signal = self.pico.convert2volts(signal, vrange)
        if irange is not None: signal = signal*irange
        self.save_signal(savepath, signal_name, signal)
        
        
    
    def reinitialize_liveplot(self, savepath):
        ''' 
        If a cycle is terminated (end of the discharge) save the voltage and 
        current picture and reinitialize the figure.
        '''
        self.liveplot.fig.savefig(savepath+'/V_I_plot')
        self.liveplot.initialize_arrays()

    
    def save_data(self, is_array_full=False):
        if self.debug: print('Entered in saving function')
        # Decide saving path and folder names based on the technique ongoing
        if self.is_cycling:
            savepath = f'{self.experiment_info.deis_directory}/{self.experiment_info.project_name}/{self.experiment_info.cell_name}/{self.experiment_info.experiment_name}CH{self.num}/cycle{self.cycle_number:03d}/'
            if is_array_full:
                # Check the current technique to add at the end of the file name
                if self.current_tech_id == 155:
                    if self.sequence[self.current_tech_index].user_params.current > 0:
                        savepath = savepath + f'{self.current_tech_index}_CP_charge'
                        if self.verbosity>1: print(f'> CH{self.num} msg: ')
                    elif self.sequence[self.current_tech_index].user_params.current < 0:
                        savepath = savepath + f'{self.current_tech_index}_CP_discharge'    
                elif self.current_tech_id == 101:
                    savepath = savepath + f'{self.current_tech_index}_CA_charge'
                elif self.current_tech_id == 100:
                    savepath = savepath + f'{self.current_tech_index}_rest'
                savepath = savepath + f'_part{self.part_count}'
                self.part_count += 1
                if self.debug: print(f'Current part: {self.part_count}')
            else:
                # Check the current technique to add at the end of the file name
                if self.current_tech_id == 155:
                    if self.sequence[self.current_tech_index].user_params.current > 0:
                        savepath = savepath + f'{self.current_tech_index}_CP_charge'
                        if self.verbosity>1: print(f'> CH{self.num} msg: ')
                    elif self.sequence[self.current_tech_index].user_params.current < 0:
                        savepath = savepath + f'{self.current_tech_index}_CP_discharge'    
                elif self.current_tech_id == 101:
                    savepath = savepath + f'{self.current_tech_index}_CA_charge'
                elif self.current_tech_id == 100:
                    savepath = savepath + f'{self.current_tech_index}_rest'
        else :
            savepath = f'{self.experiment_info.deis_directory}/{self.experiment_info.project_name}/{self.experiment_info.cell_name}/{self.experiment_info.experiment_name}CH{self.num}/'
            if is_array_full:
                savepath = savepath + f'/part{self.part_count}_' #!!! Add the final part number when called normally
                self.part_count += 1
        # Create the path
        Path(savepath).mkdir(parents=True, exist_ok=True)
        # Start saving the signals in multithread
        # Copy data to a different memory to beeing able to re-initialize the 
        # class
        if self.pico is not None:
            # !!! Get the last data from picoscope before resetting
            final_index = self.pico.nextSample # Save last index of big buffer
            # self.pico.nextSample = 0  # Reinitilized index to point big buffer
            # self.pico.stop()
            vrange_Ewe = self.pico.channels['A'].vrange
            vrange_I   = self.pico.channels['B'].vrange
            # irange = self.sequence[self.current_tech_index].user_params.i_range
            irange = self.i_range
            self.Ewe_saving = np.copy(self.pico.channels['A'].buffer_total[0:final_index])
            self.I_saving   = np.copy(self.pico.channels['B'].buffer_total[0:final_index])
            self.time_experiment_saving = np.multiply(self.pico.dt_in_seconds, np.arange(self.Ewe_saving.size), dtype = 'float32')
            save_Ewe_thread  = Thread(target=(self.save_pico_signal), args=[savepath,'voltage',self.Ewe_saving,  vrange_Ewe, None])
            save_I_thread    = Thread(target=(self.save_pico_signal), args=[savepath,'current',self.I_saving,  vrange_I, irange])
            save_time_thread = Thread(target=(self.save_signal), args=[savepath,'time_experiment', self.time_experiment_saving])
            self.pico.reinitialize_channels()
            # self.pico.run_streaming_non_blocking()
            save_Ewe_thread.start()
            save_I_thread.start()
            save_time_thread.start()
            
        else:
            self.Ewe_saving = np.copy(self.Ewe[0:self.next_sample])
            self.I_saving = np.copy(self.I[0:self.next_sample])
            # self.time_experiment_saving = np.copy(self.time_experiment[0:self.next_sample])
            save_Ewe_thread  = Thread(target=(self.save_signal), args=[savepath,'voltage',self.Ewe_saving])
            save_I_thread    = Thread(target=(self.save_signal), args=[savepath,'current',self.I_saving])
            # save_time_thread = Thread(target=(self.save_signal), args=[savepath,'time_experiment', self.time_experiment_saving])
            save_Ewe_thread.start()
            save_I_thread.start()
            # save_time_thread.start()
        # At the end of the discahrge save current cycle liveplot and reinitialize it 
        # Change the behaviour in case of non cycling experiment
        if is_array_full == False and self.current_tech_id == 155 and self.sequence[self.current_tech_index].user_params.current < 0:
            self.reinitialize_liveplot(os.path.dirname(savepath))
            self.cycle_number = self.cycle_number + 1
        print(f'>CH{self.num} msg: data saved')