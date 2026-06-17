import logging
import time
import json
from collections.abc import Sequence
from datetime import datetime
from threading import Thread
import numpy as np

from dataclasses import asdict

from pyeclab.api.tech_types import TECH_ID

from pyeclab.device import BiologicDevice

from pyeclab.channel.acquisition import DataAcquisition
from pyeclab.channel.config import ChannelConfig
from pyeclab.channel.liveplot import LivePlot
from pyeclab.channel.limits import SoftwareLimitChecker
from pyeclab.channel.monitoring import SequenceMonitor
from pyeclab.channel.writers.abstractwriter import AbstractWriter
from pyeclab.channel.auxiliary_functions import end_technique
from pyeclab.techniques import custom_serialization_factory

logger = logging.getLogger("pyeclab")


# TODO
class HardwareConfig:
    "See page 153 of the manual"
    def set_CE2ground(self): ...
    def set_controlled_potential(self): ...


class Channel:
    def __init__(
        self,
        bio_device: BiologicDevice,
        channel_num: int,
        writer: AbstractWriter,
        config: ChannelConfig,
    ):
        self.bio_device = bio_device
        self.num = channel_num
        self.writer = writer
        self.config = config
        # Hardware setting
        self.acquisition = DataAcquisition(bio_device, channel_num, config)
        self.limit_checker = SoftwareLimitChecker()
        self.sequence_monitor = SequenceMonitor()
        self.running = False
        # Setup thread
        self.run_thread = Thread(target=self._run)


    # Basic methods for managing the execution

    def start(self):
        self._instantiate_writer()
        self._save_metadata()
        # Start channel on the device
        self.first_loop = True
        self.bio_device.start_channel(self.num)
        # Start collecting data from the device
        self.running = True
        self.run_thread.start()
        # Initialize liveplot
        if self.config.live_plot:
            self.start_live_plot()
        print(f"CH{self.num}: Experiment started")

    def stop(self):
        self.bio_device.stop_channel(self.num)
        # self.acquisition.poll()  # ? There shoudl be still the latest values to retrive
        self.running = False
        self.run_thread.join()    
        print(f"CH{self.num}: interrupted by the user")

    def _run(self, sleep_time=1):
        """
        Retrives latest measurement data from the BioLogic device, converts and
        saves. The sequence progression is also monitored.
        """
        logger.debug("Starting Data Loop (_retrieve_data_loop)")
        while True:
            self.current_values, self.data_info, self.latest_data = self.acquisition.poll()
            # Write latest data to open saving file
            self._write_latest_data_to_file()
            # Print latest values
            if self.config.print_values:
                self._print_current_values()
            # Break the loop if sequence is terminates
            if self.current_values.State == 0:
                self.running = False
                print(f"CH{self.num}: Measure completed.")
                break
            # Check if the technique has changed on the instrument
            if self.sequence_monitor.update(self.data_info):
                print(f"> CH{self.num} msg: new technique started ({self.data_info.TechniqueID})")
            # Stop current technique if any software limit is reached
            if self.limit_checker.check(self.current_values, self.data_info):
                print("Software limits met")  # debug print
                self.end_technique()
            # Sleep before retriving next measured data
            time.sleep(sleep_time)
        

    ## Methods for setting hardware for the experiment ##

    def set_hardware_config(self): ...

    def load_sequence(self, sequence: Sequence, ask_ok=False):
        self.sequence = sequence
        for element in sequence:
            if element.ecc_file is None or element.ecc_params is None:
                raise AttributeError(
                    f"Ecc File or Ecc Params of {type(element).__name__} are None. Did you call .make_technique() ?"
                )
        self.bio_device.load_sequence(self.num, self.sequence, display=ask_ok)

    ## Methods to interact with the instrument

    def start_live_plot(self):
        self.liveplot = LivePlot(self)

    def end_technique(self):
        end_technique(self)

    

    ## Methods for managing data collection during run ##

    def _print_current_values(self):
        print(
            f"CH{self.num} > Ewe: {self.current_values.Ewe:4.3e} V | I: {self.current_values.I:4.3e} mA | Tech_ID: {TECH_ID(self.data_info.TechniqueID).name} | Tech_indx: {self.data_info.TechniqueIndex} | loop: {self.data_info.loop}"
        )


    ## Methods for saving data and metadata (including initialization of the files)

    def _instantiate_writer(self):
        """Create the structure of the data as list and pass it to the writer,
        which in return creates the appropriate structure in a file, database or similar.
        """
        structure = ["Time/s", "Ewe/V", "I/A", "Technique_num", "Loop_num"]

        if self.config.record_ece and self.config.record_charge:
            structure.insert(3, "Ece/V")
            structure.insert(4, "Q/C")
        elif self.config.record_ece:
            structure.insert(3, "Ece/V")
        elif self.config.record_charge:
            structure.insert(3, "Q/C")

        self.writer.instantiate(structure)

    def _write_latest_data_to_file(self):
        """Format the latest data into a numpy array and pass it to the writers .write() method."""
        technique_num = self.sequence_monitor.current_tech_index * np.ones(len(self.latest_data[0]))
        loop_num = self.data_info.loop * np.ones(len(self.latest_data[0]))

        data_to_save = np.column_stack((*self.latest_data, technique_num, loop_num))

        self.writer.write(data_to_save)

    def _save_metadata(self):
        metadata_dict = {
            'Device address' : self.bio_device.address,
            'Channel num' : self.num,
            'Starting time' : datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            # not working 'Sequence' : [asdict(technique, dict_factory=custom_serialization_factory) for technique in self.sequence]
        }
        metadata_dict.update(asdict(self.config))
        if self.limit_checker.conditions:
            metadata_dict.update(
                {
                    'Software conditions' : [asdict(instance) for instance in self.limit_checker.conditions]
                }
            )
        if self.sequence_monitor.on_technique_change:
            metadata_dict.update(
                {
                    'Executed function': self.sequence_monitor.on_technique_change.__name__
                }
            )
        with open(str(self.writer.file_dir / self.writer.experiment_name) +'/metadata.json', 'w') as fp:
            json.dump(metadata_dict, fp)