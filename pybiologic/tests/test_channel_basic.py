from pybiologic.channel import Channel
from pybiologic.techniques import OCV_params, make_OCV_tech

# Create device


# Create OCV technique
ocv_params = OCV_params(10, 1, 0, 4, 0)
ocv_technique = ocv_params.make_OCV_tech(device.is_VMP3)

