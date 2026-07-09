from __future__ import annotations

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class OwlBrainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
	VERSION = 1

	async def async_step_user(self, user_input=None) -> FlowResult:
		# Only one instance allowed
		if self._async_current_entries():
			return self.async_abort(reason="single_instance_allowed")

		return self.async_create_entry(title="OwlBrain", data={})


class OwlBrainOptionsFlowHandler(config_entries.OptionsFlow):
	def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
		self.config_entry = config_entry

	async def async_step_init(self, user_input=None) -> FlowResult:
		return self.async_create_entry(title="", data={})


async def async_get_options_flow(
	config_entry: config_entries.ConfigEntry,
) -> OwlBrainOptionsFlowHandler:
	return OwlBrainOptionsFlowHandler(config_entry)
