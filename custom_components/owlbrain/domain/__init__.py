from .binary_sensor import OwlBrainBinarySensorEntity
from .button import OwlBrainButtonEntity
from .cover import OwlBrainCoverEntity
from .light import OwlBrainLightEntity
from .number import OwlBrainNumberEntity
from .select import OwlBrainSelectEntity
from .sensor import OwlBrainSensorEntity
from .switch import OwlBrainSwitchEntity

DOMAIN_HANDLERS = {
    "binary_sensor": OwlBrainBinarySensorEntity,
    "button": OwlBrainButtonEntity,
    "cover": OwlBrainCoverEntity,
    "light": OwlBrainLightEntity,
    "number": OwlBrainNumberEntity,
    "select": OwlBrainSelectEntity,
    "sensor": OwlBrainSensorEntity,
    "switch": OwlBrainSwitchEntity,
}
