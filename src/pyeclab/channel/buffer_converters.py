import numpy as np


def base(channel, buffer):
    Ewe = np.array(
        [channel.bio_device.ConvertNumericIntoSingle(buffer[i, 2]) for i in range(0, channel.data_info.NbRows)]
    )
    I = (
        np.array([channel.bio_device.ConvertNumericIntoSingle(buffer[i, 3]) for i in range(0, channel.data_info.NbRows)])
        if channel.data_info.TechniqueID != 100
        else np.array([0] * len(Ewe))
    )
    t = np.array(
        [
            (((buffer[i, 0] << 32) + buffer[i, 1]) * channel.current_values.TimeBase) + channel.data_info.StartTime
            for i in range(0, channel.data_info.NbRows)
        ]
    )
    return t, Ewe, I

def with_charge(channel, buffer):
    t, Ewe, I = base(buffer)
    q = np.array([channel.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, channel.data_info.NbRows)])
    return t, Ewe, I, q

def with_Ece(channel, buffer):
    t, Ewe, I = base(buffer)
    Ece = np.array(
        [channel.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, channel.data_info.NbRows)]
    )
    return t, Ewe, I, Ece

def with_charge_and_Ece(channel, buffer):
    t, Ewe, I = base(buffer)
    Ece = np.array(
        [channel.bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, channel.data_info.NbRows)]
    )
    q = np.array([channel.bio_device.ConvertNumericIntoSingle(buffer[i, 6]) for i in range(0, channel.data_info.NbRows)])
    return t, Ewe, I, Ece, q