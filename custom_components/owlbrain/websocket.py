import uuid

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DOMAIN


def register_ws(hass: HomeAssistant, registry):

    def async_handle_error(connection, msg, err):
        connection.send_error(msg["id"], "invalid_request", str(err))

    # ---------------- DEVICE ----------------

    @websocket_api.websocket_command({
        "type": "owlbrain/upsert_device",
        "namespace": str,
        "device_id": str,
        "data": dict,
    })
    @websocket_api.async_response
    async def upsert_device(hass, connection, msg):
        try:
            namespace = msg["namespace"]
            device_id = msg["device_id"]
            data = msg["data"]

            result = await registry.upsert_device(namespace, device_id, data)

            connection.send_result(msg["id"], result)

        except Exception as e:
            async_handle_error(connection, msg, e)

    @websocket_api.websocket_command({
        "type": "owlbrain/delete_device",
        "namespace": str,
        "device_id": str,
    })
    @websocket_api.async_response
    async def delete_device(hass, connection, msg):
        try:
            await registry.delete_device(msg["namespace"], msg["device_id"])
            connection.send_result(msg["id"], True)
        except Exception as e:
            async_handle_error(connection, msg, e)

    # ---------------- ENTITY ----------------

    @websocket_api.websocket_command({
        "type": "owlbrain/upsert_entity",
        "namespace": str,
        "entity_id": str,
        "data": dict,
    })
    @websocket_api.async_response
    async def upsert_entity(hass, connection, msg):
        try:
            namespace = msg["namespace"]
            entity_id = msg["entity_id"]
            data = msg["data"]

            result = await registry.upsert_entity(namespace, entity_id, data)

            connection.send_result(msg["id"], result)

        except Exception as e:
            async_handle_error(connection, msg, e)

    @websocket_api.websocket_command({
        "type": "owlbrain/update_entity_state",
        "namespace": str,
        "entity_id": str,
        "state": object,
    })
    @websocket_api.async_response
    async def update_entity_state(hass, connection, msg):
        try:
            result = await registry.update_entity_state(
                msg["namespace"], msg["entity_id"], msg["state"]
            )
            connection.send_result(msg["id"], result)
        except Exception as e:
            async_handle_error(connection, msg, e)

    @websocket_api.websocket_command({
        "type": "owlbrain/delete_entity",
        "namespace": str,
        "entity_id": str,
    })
    @websocket_api.async_response
    async def delete_entity(hass, connection, msg):
        try:
            await registry.delete_entity(msg["namespace"], msg["entity_id"])
            connection.send_result(msg["id"], True)
        except Exception as e:
            async_handle_error(connection, msg, e)

    # ---------------- LIST / CLEAR ----------------

    @websocket_api.websocket_command({
        "type": "owlbrain/list_all",
        "namespace": str,
    })
    @websocket_api.async_response
    async def list_all(hass, connection, msg):
        try:
            result = registry.list_all(msg.get("namespace"))
            connection.send_result(msg["id"], result)
        except Exception as e:
            async_handle_error(connection, msg, e)

    @websocket_api.websocket_command({
        "type": "owlbrain/clear",
        "namespace": str,
    })
    @websocket_api.async_response
    async def clear(hass, connection, msg):
        try:
            await registry.clear(msg.get("namespace"))
            connection.send_result(msg["id"], True)
        except Exception as e:
            async_handle_error(connection, msg, e)

    # ---------------- REGISTER ----------------

    websocket_api.async_register_command(hass, upsert_device)
    websocket_api.async_register_command(hass, delete_device)
    websocket_api.async_register_command(hass, upsert_entity)
    websocket_api.async_register_command(hass, update_entity_state)
    websocket_api.async_register_command(hass, delete_entity)
    websocket_api.async_register_command(hass, list_all)
    websocket_api.async_register_command(hass, clear)
