# OwlBrain Home Assistant Companion

Home Assistant integration that provides support for [**OwlBrain Home Assistant integration**](https://github.com/Armaell/owlbrain-homeassistant) to provide managed entities.
This integration is installable through [HACS](https://hacs.xyz/) and supports UI-based configuration via Home Assistant’s config flow.

## Installation

### Option 1 — HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Armaell&repository=owlbrain-homeassistant-companion&category=integration)

### Option 2 — Manual Installation

1. Download the latest release from the **Releases** page
2. Extract the folder `owlbrain` into: `config/custom_components/your_integration_name/`
3. Restart Home Assistant

---

## Configuration

This integration uses Home Assistant’s **config flow**, so setup happens entirely in the UI.

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Your Integration Name**
4. Follow the on-screen instructions

If the integration does not appear, try clearing your browser cache or restarting Home Assistant.

## Contributing

To run the development environement run the command
```
cd dev
docker compose up --build
```