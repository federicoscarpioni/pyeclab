from pyeclab.api.kbio_tech import ECC_parm

OCV_parm_names = {
    "duration": ECC_parm("Rest_time_T", float),
    "record_dt": ECC_parm("Record_every_dT", float),
    "record_dE": ECC_parm("Record_every_dE", float),
    "E_range": ECC_parm("E_Range", int),
    "bandwidth": ECC_parm("Bandwidth", int),
}
