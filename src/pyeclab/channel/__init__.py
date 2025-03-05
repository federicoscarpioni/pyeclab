import json
import logging
import time
from collections.abc import Sequence
from datetime import datetime
from threading import Thread

import numpy as np
from attrs import asdict

from pyeclab.api.tech_types import TECH_ID
from pyeclab.channel.config import ChannelConfig
from pyeclab.channel.liveplot import LivePlot
from pyeclab.channel.writers.abstractwriter import AbstractWriter
from pyeclab.device import BiologicDevice
from pyeclab.techniques.functions import reset_duration, set_duration_to_1s

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
        callbacks: list | None = None,
    ):
        self.bio_device = bio_device
        self.num = channel_num
        self.writer = writer
        self.config = config
        self.callbacks = [] if callbacks is None else callbacks
        self.current_tech_index = 0
        self.current_loop = 0
        # Hardware setting
        self.conditions = []
        self.is_running = False

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

        
    # This is not implemented yet, we need first to define a way of saving and 
    # loading the sequences. 
    # def import_sequence(self, json_file_path):
    #     with open("json_file_path") as sequence_json:
    #         self.sequence = json.load(sequence_json)
    #     self.bio_device.load_sequence(self.num, self.sequence)

    ## Methods for managing the execution of the experiment ##

    def start(self):
        self._instantiate_writer()
        self._save_exp_metadata()
        # self._save_sequence_json()

        # Start channel on the device
        self.first_loop = True
        self.bio_device.start_channel(self.num)

        # Start collecting data from the device
        loop_thread = Thread(target=self._retrive_data_loop)
        loop_thread.start()

        # Initialize liveplot
        if self.config.live_plot:
            self.start_live_plot()

        print(f"CH{self.num}: Experiment started")

    def stop(self):
        self.bio_device.stop_channel(self.num)
        self._get_measurement_values()  # ? There shoudl be still the latest values to retrive
        print(f"CH{self.num}: interrupted by the user")

    def start_live_plot(self):
        self.liveplot = LivePlot(self)

    def end_technique(self):
        """
        End the current technique in the sequence by replacing its original
        duration to the value of 1 second (This is a workaround for the lack
        of a specific function in the EC-Lab SDK).
        """
        logger.debug(f"From end_technique: {self.data_info.TechniqueID=}")
        logger.debug(f"From end_technique: {self.current_tech_id=}")
        self.bio_device.UpdateParameters(
            self.bio_device.device_id,
            self.num,
            self.current_tech_index,
            set_duration_to_1s(self.bio_device, self.sequence[self.current_tech_index], self.current_tech_id),
            self.sequence[self.current_tech_index].ecc_file,
        )

        self.bio_device.UpdateParameters(
            self.bio_device.device_id,
            self.num,
            self.current_tech_index,
            reset_duration(self.bio_device, self.sequence[self.current_tech_index], self.current_tech_id),
            self.sequence[self.current_tech_index].ecc_file,
        )

    def _print_current_values(self):
        print(
            f"CH{self.num} > Ewe: {self.current_values.Ewe:4.3e} V | I: {self.current_values.I:4.3e} mA | Tech_ID: {TECH_ID(self.data_info.TechniqueID).name} | Tech_indx: {self.data_info.TechniqueIndex} | loop: {self.data_info.loop}"
        )

    ## Methods for managing data collaction in the main loop ##

    def _final_actions(self):
        """
        Operations to perfom when the sequence is completed.
        """
        self.writer.close()
        # self._execute_callbacks() # removed to avoid double execution of callbacks.
        print(f"CH{self.num} > Measure terminated")

    def _retrive_data_loop(self, sleep_time=0.1):
        """
        Retrives latest measurement data from the BioLogic device, converts and
        saves. The sequence progression is also monitored.
        """
        logger.debug("Starting Data Loop (_retrieve_data_loop)")
        while True:
            self.latest_data = self._get_measurement_values()
            # Write latest data to open saving file
            self._write_latest_data_to_file()
            # Print latest values
            if self.config.print_values:
                self._print_current_values()
            # Check if the technique has changed on the instrument
            self._monitoring_sequence_progression()
            # Break the loop if sequence is terminates
            if self.current_values.State == 0:
                self._final_actions()
                break
            # Stop current technique if any software limit is reached
            if self._check_software_limits():
                print("Software limits met")  # debug print
                self.end_technique()
            # Sleep before retriving next measured data
            time.sleep(sleep_time)

    def _get_measurement_values(self):
        """Get measurement data from the instruments ADC and convert it into physical values."""
        self._get_data()
        latest_data = self._get_converted_buffer()
        return latest_data

    def _get_data(self):
        """
        When retriving latest agglomerated data from the instrument, the api will
        return three objects:
        current_values = current values of the measurement
        data_info = info on  the technique that is running and on the buffer content, e.g. TechniqueID
        data_buffer = data in a one dimension
        See the EC-Lab Development Kit manual for details on the data structures.
        """
        self.current_values, self.data_info, self.data_buffer = self.bio_device.GetData(
            self.bio_device.device_id, self.num
        )
        logger.debug(f"Got Data:\n{self.data_info}")

    def _get_converted_buffer_base(self, buffer):
        Ewe = np.array(
            [self.bio_device.ConvertNumericIntoSingle(buffer[i, 2]) for i in range(0, self.data_info.NbRows)]
        )
        I = (
            np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 3]) for i in range(0, self.data_info.NbRows)])
            if self.data_info.TechniqueID != 100
            else np.array([0] * len(Ewe))
        )
        t = np.array(
            [
                (((buffer[i, 0] << 32) + buffer[i, 1]) * self.current_values.TimeBase) + self.data_info.StartTime
                for i in range(0, self.data_info.NbRows)
            ]
        )
        return t, Ewe, I

    def _get_converted_buffer_with_charge(self, buffer):
        t, Ewe, I = self._get_converted_buffer_base(buffer)
        q = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, self.data_info.NbRows)])
        return t, Ewe, I, q

    def _get_converted_buffer_with_Ece(self, buffer):
        t, Ewe, I = self._get_converted_buffer_base(buffer)
        Ece = np.array(
            [self.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, self.data_info.NbRows)]
        )
        return t, Ewe, I, Ece

    def _get_converted_buffer_with_charge_and_Ece(self, buffer):
        t, Ewe, I = self._get_converted_buffer_base(buffer)
        Ece = np.array(
            [self.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, self.data_info.NbRows)]
        )
        q = np.array([self.bio_device.ConvertNumericIntoSingle(buffer[i, 6]) for i in range(0, self.data_info.NbRows)])
        return t, Ewe, I, Ece, q

    def _get_converted_buffer(self):
        """
        Convert digitalized signal from ADC to physical values.

        Note: Counter electrode  and AUX to be added!
        """
        buffer = np.array(self.data_buffer).reshape(self.data_info.NbRows, self.data_info.NbCols)

        if self.config.record_charge and self.config.record_ece:
            return self._get_converted_buffer_with_charge_and_Ece(buffer)
        elif self.config.record_charge:
            return self._get_converted_buffer_with_charge(buffer)
        elif self.config.record_ece:
            return self._get_converted_buffer_with_Ece(buffer)
        else:
            return self._get_converted_buffer_base(buffer)

    def _execute_callbacks(self):
        for callback in self.callbacks:
            if callable(callback):
                callback()

    def _update_sequence_trackers(self):
        """Update tech index, tech id and loop id."""
        self.current_tech_index = self.data_info.TechniqueIndex
        self.current_tech_id = self.data_info.TechniqueID
        logger.debug(f"From _update_sequence_trackers:\n{self.current_tech_id=}\n{self.data_info.TechniqueID}")
        self.current_loop = self.data_info.loop
        print(f"Loop {self.current_loop}, Technique {self.current_tech_index}, Technique ID {self.current_tech_id}")

    def _monitoring_sequence_progression(self):
        """
        This method checks when a new technique is started in the instrument. This
        can be used to add new behaviours to the application.
        """
        new_tech_index = self.data_info.TechniqueIndex
        new_tech_id = self.data_info.TechniqueID
        new_loop = self.data_info.loop

        if not self.is_running:
            self.is_running = True
            self.current_tech_id = new_tech_id

        if self.current_loop != new_loop or self.current_tech_index != new_tech_index or self.first_loop is True:
            self.first_loop = False
            self._update_sequence_trackers()
            self._execute_callbacks()
            print(f"> CH{self.num} msg: new technique started ({self.data_info.TechniqueID})")

    ## Methods for software control ##

    def set_condition(self, technique_index: int, quantity: str, operator: str, threshold: float):
        self.conditions.append((technique_index, quantity, operator, threshold))

    def _check_software_limits(self):
        """
        Check if a certain condition (< or > of a trashold value) is met for a
        value of the sampled data over a certain number of points.
        """
        for (
            technique_index,
            quantity,
            operator,
            threshold,
        ) in (
            self.conditions
        ):  # ? Can I manually add other attributes to current_values for the quantities that are missing?
            if self.data_info.TechniqueIndex == technique_index:
                quantity_value = getattr(
                    self.current_values, quantity, None
                )  # ! It works only for attributes of current_data. I need onther trick to make it work also for capacity or power
                if quantity_value is None:
                    continue
                if operator == ">" and quantity_value >= threshold:
                    return True
                elif operator == "<" and quantity_value <= threshold:
                    return True
        return False  # Do I need to keep this return?


    ## Methods for saving data
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
        technique_num = self.current_tech_index * np.ones(len(self.latest_data[0]))
        loop_num = self.data_info.loop * np.ones(len(self.latest_data[0]))

        data_to_save = np.column_stack((*self.latest_data, technique_num, loop_num))

        self.writer.write(data_to_save)

    def _save_exp_metadata(self):
        """Gather all the metadata, mainly from the techniques in the sequence, and pass it
        to the writers .write_metadata() method."""
        metadata = {}

        self.starting_time = datetime.now()
        metadata["Experiment Name"] = self.writer.experiment_name
        metadata["Start of Experiment"] = self.starting_time

        for idx, technique in enumerate(self.sequence):
            metadata["Technique"] = idx
            for k, v in asdict(technique).items():
                if not isinstance(v, datetime):
                    try:
                        str(v)
                        metadata[f"tech{idx}_{k}"] = v
                    except Exception:
                        logger.info("Metadata could not be processed. Type: %s", type(v))
                        continue

                else:
                    metadata[f"tech{idx}_{k}"] = v

        self.writer.write_metadata(metadata)