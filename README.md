# SonnenBatterie eco 6 – Home Assistant Integration

A custom **Home Assistant integration** for the **SonnenBatterie eco 6** that provides local monitoring and control via the battery's internal API.

The integration exposes battery metrics, charging states and operation modes and allows direct control of the battery from Home Assistant.

---

# Architecture

The integration follows the standard **Home Assistant DataUpdateCoordinator pattern**.

```text
SonnenBatterie
      │
      │  Local API (HTTP)
      │
      ▼
Coordinator (polling)
      │
      ├── Sensors
      │     ├─ PV Generation
      │     ├─ House Consumption
      │     ├─ SOC
      │     ├─ Charge Power
      │     ├─ Discharge Power
      │     └─ Battery Status
      │
      └── Select Entity
            └─ Operation Mode Control
```

The coordinator periodically reads battery data and distributes it to all entities.

---

# Features

## Battery Monitoring

The integration exposes the most important Sonnen metrics as sensors.

Available metrics include:

* PV generation
* House consumption
* Battery state of charge
* Charge power
* Discharge power
* Phase consumption
* Battery operation state

Example sensors:

```text
sensor.sonnenbatterie_soc
sensor.sonnenbatterie_pv_erzeugung
sensor.sonnenbatterie_hausverbrauch
sensor.sonnenbatterie_ladeleistung
sensor.sonnenbatterie_entladeleistung
sensor.sonnenbatterie_betriebsart_zahl
```

These values can be used in dashboards, automations or the Home Assistant energy panel.

---

# Battery Status Sensor

A **human readable battery state sensor** is included:

```text
sensor.sonnenbatterie_batterie_status
```

This sensor combines multiple battery metrics and displays the current battery behaviour:

Possible states:

* Auto (Idle)
* Lädt
* Entlädt
* Schnellladen
* Standby

The sensor derives its state from:

* `M06` – operation state
* `M34` – discharge power
* `M35` – charge power

This avoids having to interpret raw numeric values.

---

# Battery Mode Control

The battery operation mode can be controlled using a **select entity**:

```text
select.sonnenbatterie_modus
```

Supported modes:

| Mode                 | Description                      |
| -------------------- | -------------------------------- |
| Auto (Idle)          | Default automatic behaviour      |
| Schnellladen Auto    | Forced high-power charging       |
| Angepasst Laden      | Controlled charging              |
| Entladen             | Battery discharging              |
| Standby              | Battery inactive                 |
| Schnellladen Standby | Forced charging while in standby |

Mode changes are sent via:

```text
SetOperationMode
```

API endpoint.

---

# Sonnen API Operation States

The battery reports its internal state via **M06**.

| Code | Meaning                         |
| ---- | ------------------------------- |
| 10   | Auto / Idle                     |
| 11   | Maintenance charging            |
| 12   | Forced charging                 |
| 13   | Charging                        |
| 15   | Discharging                     |
| 20   | Standby                         |
| 22   | Forced charge (standby context) |

The integration translates these numeric codes into readable states.

---

# Example Dashboard

Typical dashboard elements include:

* Battery SOC gauge
* Charge / discharge power graph
* Battery status indicator
* Mode selector

Example layout:

```text
SOC:                74 %

Battery Status:     Lädt
Charge Power:       1450 W
Discharge Power:    0 W

Mode:               Schnellladen Auto
```

---

# Example Automations

### Prevent battery discharge during PV surplus

```yaml
automation:
  - alias: Prevent battery discharge
    trigger:
      - platform: numeric_state
        entity_id: sensor.pv_production
        above: 2000
    action:
      - service: sonnen_eco6.set_mode
        data:
          mode: "Auto (Idle)"
```

---

### Start charging when electricity price is low

```yaml
automation:
  - alias: Charge battery when price low
    trigger:
      - platform: numeric_state
        entity_id: sensor.energy_price
        below: 0.15
    action:
      - service: sonnen_eco6.set_mode
        data:
          mode: "Schnellladen Auto"
```

---

# Installation

## Manual Installation

Copy the integration into your Home Assistant configuration folder:

```text
/config/custom_components/sonnen_eco6
```

Restart Home Assistant afterwards.

---

# Configuration

Required information:

* Battery IP address
* Data port (default `7979`)
* Control port (default `3480`)
* Device number (usually `10`)

These values can be entered via the Home Assistant UI during integration setup.

---

# Limitations

The integration relies on the **local Sonnen API**, which is undocumented and may change depending on firmware versions.

Not all operation modes may be supported by every battery configuration.

---

# Disclaimer

This project is **not affiliated with or supported by Sonnen GmbH**.

Use at your own risk.

---

# Future Improvements

Planned improvements include:

* Energy dashboard integration
* additional battery diagnostics
* configurable automation helpers
* advanced charge/discharge strategies

