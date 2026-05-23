import uuid
from .const import SUPPORTED_ENTITY_TYPES, DOMAIN
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

class OwlBrainRegistry:
    def __init__(self, hass, storage, entry):
        self.hass = hass
        self.storage = storage
        self.entry = entry
        self.pending_entities = []
        self.data = {"devices": {}, "entities": {}}
        self.runtime_entities = {}
        self.adders = {}

    # ---------------- LIFECYCLE ----------------

    async def async_load(self):
        self.data = await self.storage.async_load()

    async def async_save(self):
        await self.storage.async_save(self.data)

    # ---------------- HELPERS ----------------

    def _device_key(self, namespace, device_id):
        return f"{namespace}:{device_id}"

    def _entity_key(self, namespace, entity_id):
        return f"{namespace}:{entity_id}"

    def _extract_platform(self, entity_id: str):
        if "." not in entity_id:
            raise ValueError("Invalid entity_id format, expected <domain>.<object_id>")

        domain, _ = entity_id.split(".", 1)

        if domain not in SUPPORTED_ENTITY_TYPES:
            raise ValueError(f"Unsupported platform: {domain}")

        return domain

    def _split_entity_id(self, entity_id: str):
        if "." not in entity_id:
            raise ValueError("Invalid entity_id format")

        domain, object_id = entity_id.split(".", 1)
        return domain, object_id

    # ---------------- PLATFORM REGISTRATION ----------------

    def register_adder(self, platform, adder):
        self.adders[platform] = adder

        to_create = [e for e in self.pending_entities if e["platform"] == platform]

        for entity in to_create:
            self.hass.async_create_task(self._create_runtime_entity(entity))
            self.pending_entities.remove(entity)


    async def _create_runtime_entity(self, entity):
        platform = entity["platform"]

        if platform not in self.adders:
            self.pending_entities.append(entity)
            return

        from .sensor import OwlBrainSensor
        from .binary_sensor import OwlBrainBinarySensor
        from .select import OwlBrainSelect
        from .switch import OwlBrainSwitch
        from .button import OwlBrainButton

        cls_map = {
            "sensor": OwlBrainSensor,
            "binary_sensor": OwlBrainBinarySensor,
            "select": OwlBrainSelect,
            "button": OwlBrainButton,
            "switch": OwlBrainSwitch,
        }

        entity_registry = er.async_get(self.hass)
        device_registry = dr.async_get(self.hass)

        domain, object_id = self._split_entity_id(entity["id"])

        ha_device_id = None
        if entity.get("device_id"):
            identifier = (DOMAIN, f"{entity['namespace']}:{entity['device_id']}")
            device = device_registry.async_get_device(identifiers={identifier})
            if device:
                ha_device_id = device.id

        entity_registry.async_get_or_create(
            domain=domain,
            platform=DOMAIN,
            unique_id=entity["unique_id"],
            suggested_object_id=object_id,
            config_entry=self.entry,
            device_id=ha_device_id,
        )

        ent = cls_map[platform](self, entity)

        self.runtime_entities[entity["unique_id"]] = ent

        self.adders[platform]([ent])

    # ---------------- DEVICES ----------------

    async def upsert_device(self, namespace, device_id, payload):
        key = self._device_key(namespace, device_id)
        exists = key in self.data["devices"]

        device = {
            "id": device_id,
            "namespace": namespace,
            "unique_id": str(uuid.uuid4()),
            **payload,
        }

        if exists:
            device["unique_id"] = self.data["devices"][key]["unique_id"]

        self.data["devices"][key] = device
        await self.async_save()

        device_registry = dr.async_get(self.hass)

        identifiers = {(DOMAIN, f"{namespace}:{device_id}")}

        ha_device = device_registry.async_get_device(identifiers=identifiers)

        name = device.get("name") or device_id

        if ha_device:
            device_registry.async_update_device(
                ha_device.id,
                name=name,
                manufacturer=device.get("manufacturer"),
                model=device.get("model"),
                sw_version=device.get("sw_version"),
                hw_version=device.get("hw_version"),
                serial_number=device.get("serial_number"),
                configuration_url=device.get("configuration_url"),
                suggested_area=device.get("area"),
                connections={
                    ("mac", device["mac_address"])
                } if device.get("mac_address") else None,
            )
        else:
            device_registry.async_get_or_create(
                config_entry_id=self.entry.entry_id,
                identifiers=identifiers,
                name=device.get("name"),
                manufacturer=device.get("manufacturer"),
                model=device.get("model"),
                sw_version=device.get("sw_version"),
                hw_version=device.get("hw_version"),
                serial_number=device.get("serial_number"),
                configuration_url=device.get("configuration_url"),
                suggested_area=device.get("area"),
                connections={
                    ("mac", device["mac_address"])
                } if device.get("mac_address") else None,
            )

        return {
            "action": "updated" if exists else "created",
            "data": device,
        }

    async def delete_device(self, namespace, device_id):
        key = self._device_key(namespace, device_id)
        self.data["devices"].pop(key, None)
        await self.async_save()

    # ---------------- ENTITIES ----------------

    async def upsert_entity(self, namespace, entity_id, payload):
        entity_id = entity_id.lower()
        key = self._entity_key(namespace, entity_id)

        platform = self._extract_platform(entity_id)

        if payload.get("device_id"):
            device_key = self._device_key(namespace, payload["device_id"])
            if device_key not in self.data["devices"]:
                raise ValueError("Device does not exist")

        exists = key in self.data["entities"]

        entity = {
            "id": entity_id,
            "namespace": namespace,
            "unique_id": str(uuid.uuid4()),
            "platform": platform,
            "state": None,
            **payload,
        }

        if exists:
            previous = self.data["entities"][key]

            if previous["platform"] != platform:
                raise ValueError("Cannot change entity domain")

            entity["unique_id"] = previous["unique_id"]
            entity["state"] = previous.get("state")

        self.data["entities"][key] = entity
        await self.async_save()

        entity_registry = er.async_get(self.hass)
        device_registry = dr.async_get(self.hass)

        ha_device_id = None
        if entity.get("device_id"):
            identifier = (DOMAIN, f"{namespace}:{entity['device_id']}")
            device = device_registry.async_get_device(identifiers={identifier})
            if device:
                ha_device_id = device.id

        if exists:
            ha_entity_id = entity_registry.async_get_entity_id(
                platform, DOMAIN, entity["unique_id"]
            )

            if ha_entity_id:
                entity_registry.async_update_entity(
                    ha_entity_id,
                    device_id=ha_device_id,
                )

            ent = self.runtime_entities.get(entity["unique_id"])
            if ent:
                ent.update_from_registry(entity)

        else:
            await self._create_runtime_entity(entity)

        return {
            "action": "updated" if exists else "created",
            "data": entity,
        }

    async def update_entity_state(self, namespace, entity_id, state):
        key = self._entity_key(namespace, entity_id)

        if key not in self.data["entities"]:
            raise ValueError("Entity not found")

        self.data["entities"][key]["state"] = state
        await self.async_save()

        entity = self.data["entities"][key]

        ent = self.runtime_entities.get(entity["unique_id"])
        if ent:
            ent.update_from_registry(entity)

        return entity

    async def delete_entity(self, namespace, entity_id):
        key = self._entity_key(namespace, entity_id)

        entity = self.data["entities"].pop(key, None)
        if not entity:
            return

        ent = self.runtime_entities.pop(entity["unique_id"], None)
        if ent:
            await ent.async_remove()

        entity_registry = er.async_get(self.hass)
        ha_entity_id = entity_registry.async_get_entity_id(
            entity["platform"], DOMAIN, entity["unique_id"]
        )

        if ha_entity_id:
            entity_registry.async_remove(ha_entity_id)

        if entity.get("device_id"):
            device_key = self._device_key(namespace, entity["device_id"])

            still_used = any(
                e.get("device_id") == entity["device_id"]
                for e in self.data["entities"].values()
            )

            if not still_used:
                device_registry = dr.async_get(self.hass)
                device = device_registry.async_get_device(
                    identifiers={(DOMAIN, f"{namespace}:{entity['device_id']}")}
                )

                if device:
                    device_registry.async_remove_device(device.id)

                self.data["devices"].pop(device_key, None)

        await self.async_save()


    # ---------------- LIST / CLEAR ----------------

    def list_all(self, namespace=None):
        devices = list(self.data["devices"].values())
        entities = list(self.data["entities"].values())

        if namespace:
            devices = [d for d in devices if d["namespace"] == namespace]
            entities = [e for e in entities if e["namespace"] == namespace]

        return {"devices": devices, "entities": entities}

    async def clear(self, namespace=None):
        entity_registry = er.async_get(self.hass)
        device_registry = dr.async_get(self.hass)

        for entity in list(self.data["entities"].values()):
            if namespace and entity["namespace"] != namespace:
                continue

            unique_id = entity["unique_id"]

            ent = self.runtime_entities.pop(unique_id, None)
            if ent:
                await ent.async_remove()

            ha_entity_id = entity_registry.async_get_entity_id(
                entity["platform"], DOMAIN, unique_id
            )
            if ha_entity_id:
                entity_registry.async_remove(ha_entity_id)

            key = self._entity_key(entity["namespace"], entity["id"])
            self.data["entities"].pop(key, None)

        for device in list(self.data["devices"].values()):
            if namespace and device["namespace"] != namespace:
                continue

            identifier = (DOMAIN, f"{device['namespace']}:{device['id']}")
            ha_device = device_registry.async_get_device(identifiers={identifier})

            if ha_device:
                device_registry.async_remove_device(ha_device.id)

            key = self._device_key(device["namespace"], device["id"])
            self.data["devices"].pop(key, None)

        if not namespace:
            self.runtime_entities = {}

        await self.async_save()
