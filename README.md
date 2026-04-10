# 🔧 Vibration to RPM — Industrial IoT Monitor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-C51A4A?style=for-the-badge&logo=raspberry-pi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**Real-time vibration measurement and RPM estimation for industrial machinery using a Raspberry Pi 4 and ADXL345 accelerometer.**

*Designed for eddy current separator monitoring — keeping your machine healthy, one reading at a time.*

</div>

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Hardware Components](#-hardware-components)
3. [Circuit Diagram](#-circuit-diagram)
4. [Prerequisites](#-prerequisites)
5. [Setup Instructions](#-setup-instructions)
6. [Signal Processing](#-signal-processing)
7. [Installation & Dependencies](#-installation--dependencies)
8. [Usage](#-usage)
9. [Data Collection](#-data-collection)
10. [Calibration](#-calibration)
11. [Output](#-output)
12. [Troubleshooting](#-troubleshooting)
13. [Contributing](#-contributing)
14. [References](#-references)

---

## 🌟 Project Overview

This project is an **Industrial IoT application** that measures mechanical vibrations from an **eddy current separator machine** and converts those vibrations into an estimated **RPM (Revolutions Per Minute)** reading in real time.

Eddy current separators are high-speed rotating machines used in recycling and waste-sorting industries. Monitoring their rotational speed and vibration signature is critical for:

- 🔍 **Predictive maintenance** — detect early signs of imbalance or bearing wear
- ⚠️ **Overspeed protection** — alert operators when RPM exceeds safe thresholds
- 📊 **Operational logging** — record historical vibration and RPM data for analysis

The system uses an **ADXL345 digital accelerometer** connected via **I²C** to a **Raspberry Pi 4**, continuously sampling tri-axial vibration data. A signal-processing pipeline converts raw accelerometer readings into an RMS vibration magnitude and then maps that to an RPM estimate. All data is visualized live with `matplotlib` and persisted to a CSV file.

---

## 🛠️ Hardware Components

| Component | Description | Notes |
|---|---|---|
| **Raspberry Pi 4 Model B** | Main processing unit | 2 GB RAM or higher recommended |
| **ADXL345** | 3-axis digital accelerometer | I²C address `0x53` (SDO pulled HIGH) or `0x1D` (SDO LOW) |
| **LM393** | Dual comparator IC | Optional — used for optical or magnetic RPM cross-validation |
| **Breadboard & jumper wires** | Prototyping connections | Female-to-female wires for GPIO header |
| **3.3 V / 5 V power rail** | Logic-level power | ADXL345 operates at 2.0 V – 3.6 V; use 3.3 V from Pi |
| **10 kΩ pull-up resistors** | I²C bus pull-ups | Usually not needed — Raspberry Pi has built-in pull-ups |
| **Micro SD Card (16 GB+)** | OS storage | Class 10 / UHS-I recommended |

### ADXL345 Key Specifications

| Parameter | Value |
|---|---|
| Supply voltage | 2.0 V – 3.6 V |
| Interface | I²C / SPI |
| I²C address | `0x53` (ALT ADDRESS pin HIGH) |
| Measurement range | ±2 g, ±4 g, ±8 g, **±16 g** (configurable) |
| Resolution | 10-bit (up to 13-bit in full-resolution mode) |
| Sensitivity (±16 g mode) | **3.9 mg/LSB** |
| Output data rate | 0.1 Hz – 3200 Hz |

---

## 🔌 Circuit Diagram

```
Raspberry Pi 4 (GPIO Header)          ADXL345
──────────────────────────────────    ───────────
Pin  1  → 3.3V  ───────────────────→  VCC
Pin  6  → GND   ───────────────────→  GND
Pin  3  → GPIO2 (SDA1) ────────────→  SDA
Pin  5  → GPIO3 (SCL1) ────────────→  SCL
                         ┌─────────→  CS  (tie to VCC for I²C mode)
3.3V ────────────────────┘
                         ┌─────────→  SDO (tie to VCC → address 0x53)
3.3V ────────────────────┘

Optional LM393 comparator (for optical RPM):
──────────────────────────────────────────────
Pin 11 → GPIO17 ───────────────────→  LM393 OUT
3.3V            ───────────────────→  LM393 VCC
GND             ───────────────────→  LM393 GND
IR LED + photodiode / hall sensor → LM393 inputs
```

> 💡 **Tip:** Mount the ADXL345 directly on the machine frame or motor housing using double-sided foam tape or a small M3 bolt through the mounting hole. Closer to the bearing = better signal.

---

## ✅ Prerequisites

### Hardware

- [ ] Raspberry Pi 4 (any RAM variant)
- [ ] ADXL345 breakout board
- [ ] Jumper wires (female-to-female)
- [ ] Breadboard (optional)
- [ ] Stable 5 V / 3 A USB-C power supply for the Raspberry Pi
- [ ] Monitor / SSH access to the Pi

### Software

- [ ] Raspberry Pi OS (Bullseye or later) — 32-bit or 64-bit
- [ ] Python 3.7+
- [ ] I²C enabled on the Raspberry Pi
- [ ] Git

---

## 🚀 Setup Instructions

### 1 — Enable I²C on the Raspberry Pi

```bash
sudo raspi-config
```

Navigate to **Interface Options → I2C → Enable**, then reboot:

```bash
sudo reboot
```

Verify the I²C bus is available after reboot:

```bash
ls /dev/i2c*
# Expected output: /dev/i2c-1
```

### 2 — Connect the ADXL345

Wire the sensor according to the [Circuit Diagram](#-circuit-diagram) above. After wiring, scan the I²C bus to confirm the sensor is detected:

```bash
sudo apt-get install -y i2c-tools
i2cdetect -y 1
```

You should see `53` (or `1d`) appear in the grid:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
50: -- -- -- 53 -- -- -- -- -- -- -- -- -- -- -- --
```

### 3 — Clone the Repository

```bash
git clone https://github.com/DawodRhman/Vibration-to-Rpm.git
cd Vibration-to-Rpm
```

### 4 — Install Dependencies

```bash
pip3 install -r requirements.txt
```

> See [Installation & Dependencies](#-installation--dependencies) for the full package list.

---

## 📡 Signal Processing

The pipeline from raw sensor data to RPM follows these steps:

```
┌─────────────────┐     I²C     ┌──────────────────┐
│  ADXL345 sensor │ ──────────→ │  Raw X, Y, Z data │  (2's complement integers)
└─────────────────┘             └──────────┬───────┘
                                           │  × 0.0039  (sensitivity, g/LSB)
                                           ▼
                               ┌──────────────────────┐
                               │  Physical acceleration │  (units: g)
                               └──────────┬───────────┘
                                          │  RMS = √(X² + Y² + Z²)
                                          ▼
                               ┌──────────────────────┐
                               │  Vibration magnitude  │  (scalar, g)
                               └──────────┬───────────┘
                                          │  RPM = vibration × conversion_factor
                                          ▼
                               ┌──────────────────────┐
                               │   Estimated RPM       │  clamped to [0, 3000]
                               └──────────────────────┘
```

### Key Parameters

| Parameter | Value | Description |
|---|---|---|
| `SENSITIVITY` | `0.0039` g/LSB | ADXL345 sensitivity in ±16 g mode |
| `conversion_factor` | `100` | Linear scaling from vibration magnitude to RPM |
| `RPM_THRESHOLD` | `3000` | Maximum expected / safe RPM |
| Sampling interval | `0.1 s` | ~10 Hz data acquisition rate |

### Why RMS?

The **Root Mean Square** of the three acceleration axes gives a single, rotation-invariant measure of vibration energy regardless of sensor orientation:

```
vibration_rms = √(ax² + ay² + az²)
```

This metric correlates with the rotational energy of the machine and can be mapped to RPM through a calibrated linear or non-linear function.

---

## 📦 Installation & Dependencies

### `requirements.txt`

```
smbus2>=0.4.2
numpy>=1.21.0
matplotlib>=3.4.0
```

Install all dependencies at once:

```bash
pip3 install smbus2 numpy matplotlib
```

| Package | Purpose |
|---|---|
| `smbus` / `smbus2` | I²C communication with the ADXL345 |
| `numpy` | Fast numerical operations (RMS calculation) |
| `matplotlib` | Real-time dual-axis plotting |
| `csv` *(stdlib)* | Writing data to CSV files |
| `datetime` *(stdlib)* | Timestamping each reading |

---

## ▶️ Usage

Run the main script (requires I²C access — may need `sudo` on some Pi OS versions):

```bash
python3 pro.py
```

Or, if you need elevated I²C permissions:

```bash
sudo python3 pro.py
```

### What Happens at Runtime

1. The ADXL345 is initialized in **measure mode** with **±16 g range**.
2. A live `matplotlib` window opens with two y-axes:
   - 🔴 **Left axis** — RPM (scaled 0–3000)
   - 🔵 **Right axis** — Vibration magnitude (g)
3. Each reading is printed to the console:
   ```
   DateTime: 2024-03-15 14:22:03  Vibration: 0.0842  Scaled RPM: 842.0
   ```
4. A CSV file (`rpm_data.csv`) is updated with every reading.
5. Press **Ctrl+C** to exit gracefully.

---

## 📂 Data Collection

Measurement data is automatically saved to `rpm_data.csv` in the working directory.

### CSV Format

```csv
DateTime,Time,RPM,Vibration
2024-03-15 14:22:03,1710508923.45,842.0,0.0842
2024-03-15 14:22:04,1710508924.55,956.0,0.0956
...
```

| Column | Type | Description |
|---|---|---|
| `DateTime` | `YYYY-MM-DD HH:MM:SS` | Human-readable timestamp |
| `Time` | Unix epoch (float) | Machine-readable timestamp |
| `RPM` | float | Estimated RPM (0–3000) |
| `Vibration` | float | RMS vibration magnitude (g) |

### Reading the CSV in Python

```python
import pandas as pd

df = pd.read_csv('rpm_data.csv')
df['DateTime'] = pd.to_datetime(df['DateTime'])
print(df.describe())
df.plot(x='DateTime', y=['RPM', 'Vibration'])
```

---

## 🎯 Calibration

The default conversion formula is a simple linear mapping:

```python
rpm = conversion_factor * vibration   # conversion_factor = 100
```

This is a starting point. For accurate readings, you should calibrate the system against a known RPM reference:

### Step-by-Step Calibration

1. **Mount the sensor** on the machine in its final position.
2. **Run the machine at a known RPM** (use a stroboscope or tachometer for reference).
3. **Record the average vibration value** from the CSV output over ~30 seconds.
4. **Calculate your `conversion_factor`**:
   ```
   conversion_factor = known_RPM / measured_vibration
   ```
5. **Repeat at 2–3 different speeds** and average the factors for a more robust calibration.
6. **Update the constant in `pro.py`**:
   ```python
   conversion_factor = <your_calculated_value>
   ```

> 🔬 For higher accuracy, consider fitting a polynomial or using a lookup table if the relationship is non-linear.

---

## 📊 Output

### Real-Time Plot

The live matplotlib window shows:

```
RPM (red)     Vibration (blue)
3000 |   /\        /\
     |  /  \  /\  /  \
1500 | /    \/  \/    \
     |/
   0 +──────────────────── Time (s)
```

- **Red line** — Estimated RPM
- **Blue line** — Vibration magnitude
- **Dashed red line** — Threshold alert at 3000 RPM

### Console Output

```
DateTime: 2024-03-15 14:22:03  Vibration: 0.084  Scaled RPM: 840.0
DateTime: 2024-03-15 14:22:04  Vibration: 0.091  Scaled RPM: 910.0
```

### CSV File

See [Data Collection](#-data-collection) for the CSV schema.

---

## 🔧 Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| `FileNotFoundError: /dev/i2c-1` | I²C not enabled | Run `sudo raspi-config` and enable I²C |
| `OSError: [Errno 121] Remote I/O error` | Sensor not wired correctly or wrong address | Double-check wiring; run `i2cdetect -y 1` |
| `ModuleNotFoundError: smbus` | Package not installed | `pip3 install smbus2` |
| All vibration readings are `0.0` | Sensor in standby mode | Check `initialize_accelerometer()` is called before reading |
| RPM values seem too high / low | Wrong `conversion_factor` | Perform calibration procedure |
| Plot window does not open | Display not configured | Set `DISPLAY=:0` or use `matplotlib` with `Agg` backend + file output |
| CSV file grows without bound | Write mode is `'w'` (overwrite) | This is by design — each run rewrites the file; change to `'a'` for append mode |
| `PermissionError` on I²C | User not in `i2c` group | `sudo usermod -aG i2c $USER` and re-login |

### Enable Debug Logging

Add the following at the top of `pro.py` to print raw register bytes:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🤝 Contributing

Contributions are welcome and appreciated! Whether it's a bug fix, calibration improvement, or new feature — feel free to open an issue or submit a pull request.

### How to Contribute

1. **Fork** the repository
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and add tests where applicable
4. **Commit** with a clear message
   ```bash
   git commit -m "feat: add FFT-based RPM estimation"
   ```
5. **Push** to your fork and open a **Pull Request**

### Ideas for Improvement

- [ ] FFT-based frequency analysis for more accurate RPM detection
- [ ] MQTT / InfluxDB integration for cloud dashboards
- [ ] Email / SMS alerts when RPM exceeds threshold
- [ ] Multi-sensor support (multiple ADXL345 boards)
- [ ] Web-based dashboard (Flask / Dash)
- [ ] Unit tests and CI/CD pipeline

---

## 📚 References

| Resource | Link |
|---|---|
| ADXL345 Datasheet | [Analog Devices ADXL345](https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf) |
| LM393 Datasheet | [Texas Instruments LM393](https://www.ti.com/lit/ds/symlink/lm393-n.pdf) |
| Raspberry Pi 4 Documentation | [raspberrypi.com/documentation](https://www.raspberrypi.com/documentation/) |
| Raspberry Pi I²C Guide | [pinout.xyz/i2c](https://pinout.xyz/pinout/i2c) |
| smbus2 Library | [PyPI: smbus2](https://pypi.org/project/smbus2/) |
| NumPy Documentation | [numpy.org](https://numpy.org/doc/) |
| Matplotlib Documentation | [matplotlib.org](https://matplotlib.org/stable/contents.html) |

---

<div align="center">

Made with ❤️ by [DawodRhman](https://github.com/DawodRhman)

*If this project helped you, please consider giving it a ⭐!*

</div>
