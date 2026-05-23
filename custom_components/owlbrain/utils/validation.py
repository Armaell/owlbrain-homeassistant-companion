from __future__ import annotations

from typing import Iterable, Union, Type
from enum import Enum, IntFlag

from ..errors import OwlInvalidValueError

def ensure_bool(name: str, value):
	if isinstance(value, bool):
		return value
	raise OwlInvalidValueError(name, value, "boolean")

def ensure_int(name: str, value):
	if isinstance(value, int):
		return value
	raise OwlInvalidValueError(name, value, "integer")

def ensure_in_range(name: str, value: int, min_value: int, max_value: int):
	if not (min_value <= value <= max_value):
		raise OwlInvalidValueError(name, value, f"between {min_value} and {max_value}")
	return value

def ensure_float(name: str, value):
	if isinstance(value, (int, float)):
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
    name: str,
    value: Union[int, Iterable[str]],
    enum_cls: Type[IntFlag],
) -> int:
    """Validate feature flags as either:
    - an int bitmask
    - a list[str] of enabled feature names
    """

    if isinstance(value, int):
        return ensure_int(name, value)

    if isinstance(value, (list, tuple, set)):
        bitmask = enum_cls(0)

        for key in value:
            key_str = ensure_str(f"{name}[]", key).upper()

            try:
                feature = enum_cls[key_str]
            except KeyError:
                allowed = list(enum_cls.__members__.keys())
                raise OwlInvalidValueError(
                    f"{name}[{key}]",
                    key,
                    allowed,
                )

            bitmask |= feature

        return bitmask.value

    raise OwlInvalidValueError(
        name,
        value,
        "integer or list[str]",
    )
