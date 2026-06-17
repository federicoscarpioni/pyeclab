import numpy as np

def base(bio_device, data_info, current_values, buffer):
    Ewe = np.array(
        [bio_device.ConvertNumericIntoSingle(buffer[i, 2]) for i in range(0, data_info.NbRows)]
    )
    I = (
        np.array([bio_device.ConvertNumericIntoSingle(buffer[i, 3]) for i in range(0, data_info.NbRows)])
        if data_info.TechniqueID != 100
        else np.array([0] * len(Ewe))
    )
    t = np.array(
        [
            (((buffer[i, 0] << 32) + buffer[i, 1]) * current_values.TimeBase) + data_info.StartTime
            for i in range(0, data_info.NbRows)
        ]
    )
    return t, Ewe, I

def with_charge(bio_device, data_info, current_values, buffer):
    t, Ewe, I = base(bio_device, data_info, current_values, buffer)
    if data_info.TechniqueID == 100:
        q = np.array([bio_device.ConvertNumericIntoSingle(buffer[i, 3]) for i in range(0, data_info.NbRows)])
    else:
        q = np.array([bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, data_info.NbRows)])
    return t, Ewe, I, q

def with_Ece(bio_device, data_info, current_values, buffer):
    t, Ewe, I = base(bio_device, data_info, current_values, buffer)
    if data_info.TechniqueID == 100:
        Ece = np.array(
            [bio_device.ConvertNumericIntoSingle(buffer[i, 3]) for i in range(0, data_info.NbRows)]
        )
    else:
        Ece = np.array(
            [bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, data_info.NbRows)]
        )
    return t, Ewe, I, Ece

def with_charge_and_Ece(bio_device, data_info, current_values, buffer):
    t, Ewe, I = base(bio_device, data_info, current_values, buffer)
    if data_info.TechniqueID == 100:
        Ece = np.array(
            [bio_device.ConvertNumericIntoSingle(buffer[i, 3]) for i in range(0, data_info.NbRows)]
        )
        q = np.array([bio_device.ConvertNumericIntoSingle(buffer[i, 4]) for i in range(0, data_info.NbRows)])
    else:
        Ece = np.array(
            [bio_device.ConvertNumericIntoSingle(buffer[i, 5]) for i in range(0, data_info.NbRows)]
        )
        q = np.array([bio_device.ConvertNumericIntoSingle(buffer[i, 6]) for i in range(0, data_info.NbRows)])
    return t, Ewe, I, Ece, q
