# 🍄 Grow Environment — Pink Oyster (*Pleurotus djamor*)

**Spawn:** 1 lb colonized grain spawn bag

---

## Colonization Stage *(no Pi involved)*

| Parameter | Value |
|---|---|
| Substrate | Straw only |
| Bags | 3× zip bags (33 × 39 cm) |
| Location | Kitchen cabinet above appliance — dark |
| Temperature | ~27–30°C |
| Duration | 7–14 days |

---

## Fruiting Chamber *(Pi monitored)*

**Enclosure:** Open cubicle 1 m × 1 m × 1 m

| Component | Details |
|---|---|
| Containers | Plastic with drainage holes, elevated from floor |
| Heating | Ceramic heater 75 W — ambient air target 24–28°C |
| Substrate heat | Heating mat with dedicated sensor — substrate ~25°C |
| Humidification | 2× Micro USB Ultrasonic Atomizer (108 KHz), continuous self-duty-cycling 5 s on / 5 s off |
| Humidity check | Analog hygrometer (visual cross-check) |
| Airflow | 40 mm USB fan, low speed, continuous |
| Light | 12 h/day cycle — basement location, one small window (low ambient lux) |

---

## Pi Monitoring Targets

| Parameter | Target |
|---|---|
| Relative humidity | 80–85% RH |
| Temperature | 24–28°C |

---

## Hardware Redesign Plan

The Raspberry Pi served its purpose well — it validated the monitoring approach, identified key environmental issues (humidity, CO₂, temperature), and provided a live dashboard. However, for a small single-chamber grow it is overkill:

- Wiring and powering the Pi adds unnecessary complexity
- Each USB-controlled device needs its own relay
- Maintaining a full Linux system for what is essentially on/off control is disproportionate effort

**The plan is to replace the Pi with independent, dedicated hardware units** — each handling one function, self-contained, plug-and-play, and widely available on Amazon at low cost:

| Function | Current (Pi) | Replacement |
|---|---|---|
| Temp + humidity monitoring & humidifier control | SHT31 + GPIO relay + Python | Dedicated temperature/humidity controller with built-in relay (e.g. Inkbird IBS-TH2, or similar) |
| Humidifier switching | USB power switch + GPIO | Humidity controller with outlet relay — no wiring needed |
| Light cycle | Manual / Pi timer | Plug-in digital timer (mechanical or digital, ~$10) |
| Visual inspection | Pi Camera + HTTP server | Standalone Wi-Fi camera (optional, no maintenance) |

**Benefits of dedicated units:**
- No OS to maintain, no SD card corruption risk
- Each unit is independently powered — one failure doesn't affect others
- No custom code required — configure via front panel buttons
- Significantly less wiring

> The Pi codebase in this repository documents the v1 monitoring approach and remains as a reference. It will not be actively developed further.

---

## Fruiting Color Observations

**Symptom:** Pink Oysters fruit pale/cream rather than vivid pink.

**Root cause: temperature.** The pink pigment in *P. djamor* is heat-sensitive. At substrate temperatures of 25°C+ (amplified by the heating mat), pigment degrades faster during cap development. Light is **not** a factor here — the basement location keeps ambient lux very low.

**Key finding:** Heating mats are beneficial during colonization but unnecessary during fruiting — the mycelium is already fully colonized and the substrate retains heat well at ambient 25°C.

### Recommendations for more vivid pink color

| Action | Expected effect |
|---|---|
| Turn off / reduce heating mats during fruiting | Lowers microclimate temp at pin sites |
| Target fruiting chamber temp 20–23°C | Strongest single factor for pigment retention |
| Harvest earlier (caps still slightly cupped) | Color is always more vivid before caps fully flatten |

> **Note:** Pale color is purely cosmetic. Flavor, texture, and yield are unaffected. Fruiting warm trades color for faster growth — a valid tradeoff for *P. djamor*.

---

## Pin Abortion Observations

**Symptom:** Many tiny pins form but fail to develop into full fruiting bodies.

**Primary cause: CO₂ accumulation / insufficient fresh air exchange (FAE).** High CO₂ at the substrate surface is the #1 trigger for pin abort in oyster mushrooms. Contributing factors in this setup:

| Factor | Mechanism |
|---|---|
| Low-speed 40 mm fan | May not move enough fresh air for a dense flush |
| Continuous ultrasonic atomizers | Fine mist displaces air, creating a stagnant CO₂-rich micro-layer at the substrate surface |
| High ambient temp 25°C+ | Accelerates mycelium respiration → more CO₂ produced locally around pins |
| Heating mat warmth from below | Upward convection can desiccate fragile young pins before they establish |
| Ultrasonic mist landing directly on pins | Cold micro-droplets can physically damage or chill tiny pins |
| RH at 80–85% | On the low end for pin survival — developing pins need closer to 90%+ RH in the immediate air layer |

### Recommendations

| Action | Expected effect |
|---|---|
| Increase fan speed or add brief strong FAE bursts a few times daily | Clears CO₂ build-up at substrate surface |
| Angle atomizers so mist does not fall directly onto substrate | Prevents pin damage from cold micro-droplets |
| Raise target RH to 88–90% during pinning phase | Supports fragile pin development |
| Turn off heating mats during fruiting | Reduces local CO₂ production and prevents desiccation from convection |

> **Note:** CO₂ and heat effects are compounding — fixing airflow alone at high temps gives partial improvement. Combining better FAE with lower substrate temperature has the strongest impact on pin survival rate.
