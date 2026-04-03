from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class OwlBrainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        return self.async_create_entry(
            title="OwlBrain",
            data={}
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OwlBrainOptionsFlow(config_entry)


class OwlBrainOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_create_entry(title="", data={})
