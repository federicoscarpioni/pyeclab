from pybiologic.api.kbio_types import E_RANGE, BANDWIDTH
import pybiologic.techniques as tech

def test_OCV_technique():

    is_VMP3 = False

    parameters = tech.OCV_params(duration = 10,
                                record_dt = 1,
                                e_range   =  E_RANGE[3],
                                bandwidth = BANDWIDTH[5])

    ocv_tech = tech.make_OCV_tech(is_VMP3, parameters)

    print('OCV technique sucefully created!')

# !!! Make for all the techniques

if name == 'main':
    test_OCV_technique()