from __future__ import annotations

from collections.abc import Iterable
from enum import Enum, IntFlag

from ..errors import OwlInvalidValueError


def ensure_bool(name: str, value):
	if isinstance(value, bool):
		return value
	raise OwlInvalidValueError(name, value, "boolean")


def ensure_int(name: str, value):
	if isinstance(value, int) and not isinstance(value, bool):
		return value
	raise OwlInvalidValueError(name, value, "integer")


def ensure_in_range(name: str, value: int, min_value: int, max_value: int):
	if not (min_value <= value <= max_value):
		raise OwlInvalidValueError(
			name, value, f"between {min_value} and {max_value}"
		)
	return value


def ensure_float(name: str, value):
	if isinstance(value, (int, float)) and not isinstance(value, bool):
		return float(value)
	raise OwlInvalidValueError(name, value, "numeric")


def ensure_str(name: str, value):
	if isinstance(value, str):
		return value
	raise OwlInvalidValueError(name, value, "string")


def ensure_in_list(name: str, value: str, allowed: set[str]):
	if value not in allowed:
		raise OwlInvalidValueError(name, value, sorted(allowed))
	return value


def ensure_in_enum(name: str, value, enum_cls: type[Enum]):
	allowed_values = {e.value for e in enum_cls}
	ensure_in_list(name, value, allowed_values)
	return value


def ensure_features_flag(
	name: str, value: int | Iterable[str], enum_cls: type[IntFlag]
) -> int:
	"""Validate feature flags given as an int bitmask or a list of names."""
	if isinstance(value, int) and not isinstance(value, bool):
		return ensure_int(name, value)

	if isinstance(value, (list, tuple, set)):
		bitmask = enum_cls(0)

		for key in value:
			key_str = ensure_str(f"{name}[]", key).upper()

			try:
				feature = enum_cls[key_str]
			except KeyError as err:
				allowed = list(enum_cls.__members__.keys())
				raise OwlInvalidValueError(
					f"{name}[{key}]", key, allowed
				) from err

			bitmask |= feature

		return bitmask.value

	raise OwlInvalidValueError(name, value, "integer or list[str]")
