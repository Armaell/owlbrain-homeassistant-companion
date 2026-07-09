DOMAIN = "owlbrain"

STORAGE_KEY = f"{DOMAIN}_storage"
STORAGE_VERSION = 1

PLATFORMS = [
	"binary_sensor",
	"button",
	"cover",
	"light",
	"number",
	"select",
	"sensor",
	"switch",
]

WS_MESSAGE_VERSION = 1

# Unique IDs formats
UNIQUE_ID_DEVICE = "owlbrain:{namespace}:{device_id}"
UNIQUE_ID_ENTITY = "owlbrain:{namespace}:{entity_id}"
