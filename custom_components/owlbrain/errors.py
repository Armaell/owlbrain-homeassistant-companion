from __future__ import annotations


class OwlError(Exception):
	code = "unknown_error"
	message = ""


class OwlDeviceNotFoundError(OwlError):
	code = "device_not_found"

	def __init__(self, device_id):
		self.message = f"Device {device_id} not found"


class OwlEntityNotFoundError(OwlError):
	code = "entity_not_found"

	def __init__(self, entity_id):
		self.message = f"Entity '{entity_id}' not found"


class OwlPlatformNotReadyError(OwlError):
	code = "platform_not_ready"

	def __init__(self, domain):
		self.message = f"Platform not ready for domain '{domain}'"


class OwlUnsupportedDomainError(OwlError):
	code = "unsupported_domain"

	def __init__(self, domain):
		from .domain import DOMAIN_HANDLERS

		available = ", ".join(DOMAIN_HANDLERS.keys())
		self.message = (
			f"Domain '{domain}' not found. Supported domains are: {available}"
		)


class OwlNamespaceCollisionError(OwlError):
	code = "namespace_collision"

	def __init__(self, id_: str, existing_namespace: str):
		self.message = (
			f"'{id_}' already exists in namespace '{existing_namespace}'"
		)


class OwlInvalidValueError(OwlError):
	code = "invalid value"

	def __init__(self, field_name: str, value, expected):
		self.message = (
			f"Invalid {field_name} value {value}. Expected {expected}"
		)
