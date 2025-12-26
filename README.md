# SonnenBatterie eco 6.0 (local HTTP) – Home Assistant Custom Integration

This custom integration polls the Sonnen eco 6.0 local HTTP endpoints (port 7979) and controls operation mode via the controller endpoint (port 3480).

## Install (manual)
Copy `custom_components/sonnen_eco6` into your Home Assistant `config/custom_components/` folder and restart Home Assistant.

## Install (HACS)
Add this repository as a custom repository in HACS (type: Integration), then install.

## Setup
Settings → Devices & Services → Add Integration → **SonnenBatterie eco 6.0**

## Energy Dashboard
The integration provides **Power (W)**. For the Energy Dashboard you need **Energy (kWh)**.
Create kWh sensors via the built-in `integration` helper (Riemann sum) using:
- Battery charging power (M35)
- Battery discharging power (M34)

## Notes
- `DeviceNum` is auto-detected from the controller if possible. If not, it falls back to `10`.
