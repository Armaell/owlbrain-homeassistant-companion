from collections.abc import Iterator
from typing import Any
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: Any) -> None:
	"""Enable custom integrations."""
	_ = enable_custom_integrations


@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture() -> Iterator[None]:
	"""Skip notification calls."""
	with (
		patch("homeassistant.components.persistent_notification.async_create"),
		patch("homeassistant.components.persistent_notification.async_dismiss"),
	):
		yield
