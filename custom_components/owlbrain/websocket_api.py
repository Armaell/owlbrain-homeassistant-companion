from __future__ import annotations

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, WS_MESSAGE_VERSION
from .errors import OwlError
from .manager import OwlBrainManager


def async_register_websocket_api(hass: HomeAssistant, manager: OwlBrainManager):
	"""Register all websocket commands."""
	websocket_api.async_register_command(hass, handle_get_version)

	websocket_api.async_register_command(hass, handle_subscribe)
	websocket_api.async_register_command(hass, handle_unsubscribe)

	websocket_api.async_register_command(hass, handle_list_devices)
	websocket_api.async_register_command(hass, handle_upsert_device)
	websocket_api.async_register_command(hass, handle_delete_device)

	websocket_api.async_register_command(hass, handle_list_entities)
	websocket_api.async_register_command(hass, handle_upsert_entity)
	websocket_api.async_register_command(hass, handle_update_entity)
	websocket_api.async_register_command(hass, handle_delete_entity)


@websocket_api.websocket_command({"type": "owlbrain/version"})
@websocket_api.async_response
async def handle_get_version(hass, connection, msg):
	connection.send_result(msg["id"], {"version": WS_MESSAGE_VERSION})


@websocket_api.websocket_command(
	{"type": "owlbrain/subscribe", "namespace": str}
)
@callback
def handle_subscribe(hass, connection, msg):
	"""Enable this connection to receive `owlbrain_entity_action` messages.

	Those are sent when a user interacts with an entity created by this
	component. Client will only receive events on entities created with
	the same namespace.

	This also marks this connection as active. Until the subscription,
	all entities will be marked as unavailable.
	"""
	namespace = msg["namespace"]
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]
	manager.broadcaster.add(namespace, connection)

	connection.subscriptions[msg["id"]] = lambda: manager.broadcaster.remove(
		namespace, connection
	)

	connection.send_result(msg["id"], {"version": WS_MESSAGE_VERSION})


@websocket_api.websocket_command(
	{"type": "owlbrain/unsubscribe", "namespace": str}
)
@callback
def handle_unsubscribe(hass, connection, msg):
	"""Stop this connection from receiving `owlbrain_entity_action` messages.

	Scoped to the given namespace. Also marks all its entities unavailable.
	"""
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]
	manager.broadcaster.remove(msg["namespace"], connection)

	connection.send_result(msg["id"], {"version": WS_MESSAGE_VERSION})


@websocket_api.websocket_command(
	{"type": "owlbrain/list_devices", "namespace": str, "entity_id": str}
)
@websocket_api.async_response
async def handle_list_devices(hass, connection, msg):
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]

	try:
		devices = await manager.store.get_devices(msg["namespace"])
		ids = [key[1] for key in devices]
		connection.send_result(
			msg["id"], {"version": WS_MESSAGE_VERSION, "devices": ids}
		)

	except OwlError as err:
		connection.send_error(msg["id"], err.code, err.message)
	except Exception as err:
		connection.send_error(msg["id"], "list_device_failed", str(err))


@websocket_api.websocket_command(
	{
		"type": "owlbrain/upsert_device",
		"namespace": str,
		"device_id": str,
		"metadata": dict,
	}
)
@websocket_api.async_response
async def handle_upsert_device(hass, connection, msg):
	"""Create a device if needed, then overwrite its metadata.

	Available metadata fields:
	- connections
	- manufacturer
	- model
	- name
	- sw_version
	- hw_version
	- serial_number
	- via_device
	- suggested_area
	- configuration_url
	"""
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]

	try:
		namespace, device_id = msg["namespace"], msg["device_id"]
		device, action = await manager.devices.upsert(
			namespace, device_id, msg["metadata"]
		)

		connection.send_result(
			msg["id"],
			{"version": WS_MESSAGE_VERSION, "device": device, "action": action},
		)

	except OwlError as err:
		connection.send_error(msg["id"], err.code, err.message)
	except Exception as err:
		connection.send_error(msg["id"], "internal_error", str(err))


@websocket_api.websocket_command(
	{"type": "owlbrain/delete_device", "namespace": str, "device_id": str}
)
@websocket_api.async_response
async def handle_delete_device(hass, connection, msg):
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]

	try:
		await manager.devices.delete(msg["namespace"], msg["device_id"])
		connection.send_result(msg["id"], {"version": WS_MESSAGE_VERSION})

	except OwlError as err:
		connection.send_error(msg["id"], err.code, err.message)
	except Exception as err:
		connection.send_error(msg["id"], "internal_error", str(err))


@websocket_api.websocket_command(
	{"type": "owlbrain/list_entities", "namespace": str, "entity_id": str}
)
@websocket_api.async_response
async def handle_list_entities(hass, connection, msg):
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]

	try:
		entities = await manager.store.get_entities(msg["namespace"])
		ids = [key[1] for key in entities]
		connection.send_result(
			msg["id"], {"version": WS_MESSAGE_VERSION, "entities": ids}
		)

	except OwlError as err:
		connection.send_error(msg["id"], err.code, err.message)
	except Exception as err:
		connection.send_error(msg["id"], "list_entities_failed", str(err))


@websocket_api.websocket_command(
	{
		"type": "owlbrain/upsert_entity",
		"namespace": str,
		"entity_id": str,
		"metadata": dict,
	}
)
@websocket_api.async_response
async def handle_upsert_entity(hass, connection, msg):
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]

	try:
		namespace, entity_id = msg["namespace"], msg["entity_id"]
		entity, action = await manager.entities.upsert(
			namespace, entity_id, msg["metadata"]
		)

		connection.send_result(
			msg["id"],
			{"version": WS_MESSAGE_VERSION, "entity": entity, "action": action},
		)

	except OwlError as err:
		connection.send_error(msg["id"], err.code, err.message)
	except Exception as err:
		connection.send_error(msg["id"], "upsert_entity_failed", str(err))


@websocket_api.websocket_command(
	{
		"type": "owlbrain/update_entity",
		"namespace": str,
		"entity_id": str,
		"data": dict,
	}
)
@websocket_api.async_response
async def handle_update_entity(hass, connection, msg):
	"""Create an entity if needed, then overwrite its metadata.

	Generic metadata fields:
	- name
	- entity_category
	- icon
	- entity_picture
	- available

	Additional metadata fields may be available per entity domain
	"""
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]

	try:
		res = await manager.entities.update_data(
			msg["namespace"], msg["entity_id"], msg["data"]
		)
		connection.send_result(
			msg["id"], {"version": WS_MESSAGE_VERSION, "result": res}
		)

	except OwlError as err:
		connection.send_error(msg["id"], err.code, err.message)
	except Exception as err:
		connection.send_error(msg["id"], "update_entity_failed", str(err))


@websocket_api.websocket_command(
	{"type": "owlbrain/delete_entity", "namespace": str, "entity_id": str}
)
@websocket_api.async_response
async def handle_delete_entity(hass, connection, msg):
	manager: OwlBrainManager = hass.data[DOMAIN]["manager"]

	try:
		await manager.entities.delete(msg["namespace"], msg["entity_id"])
		connection.send_result(msg["id"], {"version": WS_MESSAGE_VERSION})

	except OwlError as err:
		connection.send_error(msg["id"], err.code, err.message)
	except Exception as err:
		connection.send_error(msg["id"], "delete_entity_failed", str(err))
