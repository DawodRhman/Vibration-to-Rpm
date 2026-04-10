# ⚙️ Vibration to RPM — IoT Sensor Data Acquisition

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python" alt="Python 3.7+"/>
  <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi%204-red?style=for-the-badge&logo=raspberry-pi" alt="Raspberry Pi 4"/>
  <img src="https://img.shields.io/badge/Sensor-ADXL345-green?style=for-the-badge" alt="ADXL345"/>
  <img src="https://img.shields.io/badge/Protocol-I2C-orange?style=for-the-badge" alt="I2C"/>
  <img src="https://img.shields.io/badge/License-MIT-lightgrey?style=for-the-badge" alt="MIT License"/>
</p>

> **Real-time vibration monitoring and RPM estimation for industrial machinery using an ADXL345 accelerometer and Raspberry Pi 4.**  
> Designed for use with eddy current separators and similar rotating equipment.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [System Architecture](#-system-architecture)
3. [Hardware Requirements](#-hardware-requirements)
4. [Hardware Setup & Wiring](#-hardware-setup--wiring)
5. [Software Requirements](#-software-requirements)
6. [Installation & Setup](#-installation--setup)
7. [Signal Processing](#-signal-processing)
8. [Calibration](#-calibration)
9. [Usage](#-usage)
10. [Data Collection](#-data-collection)
11. [Output Format](#-output-format)
12. [Troubleshooting](#-troubleshooting)
13. [Performance Metrics](#-performance-metrics)
14. [Future Improvements](#-future-improvements)
15. [References](#-references)

---

## 🔍 Project Overview

This project provides a lightweight, real-time **vibration-to-RPM conversion system** built on a Raspberry Pi 4. It is designed to monitor rotating machinery — particularly **eddy current separators** used in recycling and industrial material processing.

### What it does

| Feature | Details |
|---------|---------|
| 📡 **Data Acquisition** | Reads 3-axis acceleration from ADXL345 via I2C |
| 🔢 **Vibration Analysis** | Computes RMS magnitude from X, Y, Z axes |
| 🔄 **RPM Estimation** | Converts vibration intensity to RPM using a linear model |
| 📊 **Live Plotting** | Dual-axis real-time chart (RPM + Vibration vs. Time) |
| 💾 **Data Logging** | Saves timestamped records to `rpm_data.csv` |
| 🚨 **Threshold Alert** | Visual alert when RPM exceeds 3,000 RPM |

### Application Context

Eddy current separators use rapidly rotating magnetic rotors (typically 1,000–4,000 RPM). Monitoring rotor vibration provides indirect RPM measurements without physical contact — enabling **non-invasive predictive maintenance**.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIBRATION-TO-RPM SYSTEM                       │
│                                                                   │
│  ┌──────────────┐    I2C (SDA/SCL)   ┌──────────────────────┐   │
│  │  ADXL345     │◄──────────────────►│   Raspberry Pi 4     │   │
│  │ Accelerometer│                    │                      │   │
│  │  (0x53)      │                    │  ┌────────────────┐  │   │
│  └──────────────┘                    │  │  pro.py        │  │   │
│                                      │  │                │  │   │
│  ┌──────────────┐    GPIO (Digital)  │  │ ┌────────────┐ │  │   │
│  │   LM393      │◄──────────────────►│  │ │ Accel Read │ │  │   │
│  │ Speed Sensor │                    │  │ ├────────────┤ │  │   │
│  │  (Optional)  │                    │  │ │  RMS Calc  │ │  │   │
│  └──────────────┘                    │  │ ├────────────┤ │  │   │
│                                      │  │ │ RPM Convert│ │  │   │
│  ┌──────────────┐                    │  │ ├────────────┤ │  │   │
│  │ Eddy Current │                    │  │ │ Live Plot  │ │  │   │
│  │  Separator   │                    │  │ ├────────────┤ │  │   │
│  │  (Subject)   │                    │  │ │ CSV Logger │ │  │   │
│  └──────────────┘                    │  │ └────────────┘ │  │   │
│                                      │  └────────────────┘  │   │
│                                      └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Vibration (Physical) → ADXL345 (ADC) → I2C Bus → RPi 4 (Python)
  → RMS Calculation → RPM Estimation → Live Plot + CSV Log
```

---

## 🔩 Hardware Requirements

### Core Components

| Component | Model | Specification | Role |
|-----------|-------|---------------|------|
| **Microcomputer** | Raspberry Pi 4 Model B | 4GB RAM, Broadcom BCM2711 | Main processing unit |
| **Accelerometer** | ADXL345 | ±16g, 13-bit, I2C/SPI | Vibration sensing |
| **Speed Sensor** | LM393 (optional) | 5V comparator module | Digital pulse reference |
| **Power Supply** | 5V / 3A USB-C | For RPi 4 | Power |
| **Breadboard & Wires** | Standard jumper wires | — | Prototyping |

### Raspberry Pi 4 — Key Specs

```
┌──────────────────────────────────────────┐
│          Raspberry Pi 4 Model B          │
│                                          │
│  CPU   : Cortex-A72 (ARM v8) 1.8 GHz    │
│  RAM   : 1 / 2 / 4 / 8 GB               │
│  I2C   : 2× hardware I2C buses           │
│  GPIO  : 40-pin header                   │
│  OS    : Raspberry Pi OS (64-bit)        │
└──────────────────────────────────────────┘
```

### ADXL345 Accelerometer — Key Specs

```
┌──────────────────────────────────────────┐
│               ADXL345                    │
│                                          │
│  Interface  : I2C (up to 400 kHz)        │
│  I2C Addr   : 0x53 (SDO low)            │
│               0x1D (SDO high)            │
│  Resolution : 13-bit                     │
│  Range      : ±2g / ±4g / ±8g / ±16g    │
│  Sensitivity: 3.9 mg/LSB (at ±16g)      │
│  Data Rate  : 0.1 Hz – 3200 Hz          │
│  Supply     : 2.0V – 3.6V               │
└──────────────────────────────────────────┘
```

### LM393 Speed Sensor — Key Specs

```
┌──────────────────────────────────────────┐
│               LM393 Module               │
│                                          │
│  Comparator : LM393 dual comparator      │
│  Output     : Digital HIGH/LOW           │
│  Supply     : 3.3V – 5V                 │
│  Use case   : Hall effect / IR slot disc │
└──────────────────────────────────────────┘
```

---

## 🔌 Hardware Setup & Wiring

### ADXL345 to Raspberry Pi 4 — I2C Wiring

```
ADXL345 Pin        Raspberry Pi 4 Pin
───────────        ──────────────────
VCC    ──────────► Pin 1  (3.3V Power)
GND    ──────────► Pin 6  (Ground)
SDA    ──────────► Pin 3  (GPIO 2 / SDA1)
SCL    ──────────► Pin 5  (GPIO 3 / SCL1)
SDO    ──────────► Pin 9  (Ground)  ← sets I2C addr to 0x53
CS     ──────────► Pin 1  (3.3V)    ← enables I2C mode
INT1   ──────────► (Optional: Pin 11, GPIO 17)
INT2   ──────────► (Optional: Pin 13, GPIO 27)
```

> ⚠️ **Important:** The ADXL345 operates at **3.3V**. Do **not** connect to the 5V pins — this will damage the sensor.

### Raspberry Pi 4 GPIO Pinout Reference

```
                     3V3  (1) (2)  5V
     SDA1 (GPIO 2)  (3)  (4)  5V
     SCL1 (GPIO 3)  (5)  (6)  GND
          (GPIO 4)  (7)  (8)  GPIO 14
               GND  (9) (10)  GPIO 15
        (GPIO 17) (11) (12)  GPIO 18
        (GPIO 27) (13) (14)  GND
        (GPIO 22) (15) (16)  GPIO 23
               3V3 (17) (18)  GPIO 24
    ...
```

### LM393 Speed Sensor (Optional) to Raspberry Pi 4

```
LM393 Module Pin   Raspberry Pi 4 Pin
────────────────   ──────────────────
VCC    ──────────► Pin 2  (5V Power)
GND    ──────────► Pin 14 (Ground)
D0     ──────────► Pin 11 (GPIO 17)  ← Digital output
```

### Enable I2C on Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
sudo reboot
```

Verify the sensor is detected:

```bash
sudo apt-get install i2c-tools
i2cdetect -y 1
```

Expected output (ADXL345 at address `0x53`):

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
...
50: -- -- -- 53 -- -- -- -- -- -- -- -- -- -- -- --
```

---

## 💻 Software Requirements

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.7+ | Runtime |
| `smbus` / `smbus2` | ≥ 0.4 | I2C communication |
| `numpy` | ≥ 1.21 | Numerical computing, RMS |
| `matplotlib` | ≥ 3.4 | Real-time plotting |
| `csv` | stdlib | Data logging |
| `time`, `datetime` | stdlib | Timestamps |

---

## 🚀 Installation & Setup

### Step 1 — Update Your Raspberry Pi

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### Step 2 — Install Python Dependencies

```bash
# Install smbus for I2C communication
sudo apt-get install python3-smbus -y

# Install pip packages
pip3 install numpy matplotlib smbus2
```

### Step 3 — Clone the Repository

```bash
git clone https://github.com/DawodRhman/Vibration-to-Rpm.git
cd Vibration-to-Rpm
```

### Step 4 — Enable I2C Interface

```bash
sudo raspi-config
# Interface Options → I2C → Yes → Finish
sudo reboot
```

### Step 5 — Verify Hardware Connection

```bash
i2cdetect -y 1
# You should see address 0x53 in the output
```

### Step 6 — Run the Script

```bash
python3 pro.py
```

---

## 📡 Signal Processing

### Vibration Measurement

The ADXL345 outputs digital acceleration values for three axes (X, Y, Z). These raw 16-bit signed integers are scaled using the sensor's sensitivity:

```
a_x = raw_x × 0.0039  [g]
a_y = raw_y × 0.0039  [g]
a_z = raw_z × 0.0039  [g]
```

Where `0.0039 g/LSB` is the sensitivity at ±16g range (13-bit resolution).

### Root Mean Square (RMS) Vibration

The overall vibration magnitude is computed as the **Euclidean norm** (3D RMS) of the three-axis acceleration vector:

```
          ┌─────────────────────────┐
RMS =  ╲  │  a_x²  +  a_y²  +  a_z²
        ╲ └─────────────────────────┘
```

In Python:

```python
def calculate_vibration(x, y, z):
    rms = np.sqrt(x**2 + y**2 + z**2)
    return rms
```

This single scalar represents the **total vibration intensity** regardless of direction.

### RPM Conversion

The vibration magnitude is linearly mapped to RPM using a conversion factor:

```
RPM = conversion_factor × RMS_vibration
```

In the current implementation:

```python
conversion_factor = 100   # empirically tuned

def vibration_to_rpm(vibration):
    rpm = conversion_factor * vibration
    return rpm
```

RPM is clamped to the range `[0, 3000]`:

```python
scaled_rpm = min(max(avg_rpm, 0), RPM_THRESHOLD)
```

### Why Linear Conversion?

For a mechanically balanced rotating shaft with consistent loading:
- Vibration amplitude scales roughly **linearly** with rotational speed in low-RPM regimes.
- For more accurate measurements, FFT-based frequency analysis (see [Future Improvements](#-future-improvements)) is recommended.

### Sampling Rate

```
Loop delay = 0.1 s  →  Sample Rate ≈ 10 Hz
```

> The ADXL345 supports up to 3200 Hz output data rate — the software loop is the bottleneck. For higher precision, read directly from the ADXL345's FIFO buffer.

---

## 🎯 Calibration

### Step 1 — Static Baseline

Place the sensor on a **stationary surface** and record the output. With gravity, the expected reading is approximately:

```
RMS ≈ √(0² + 0² + 1²) = 1.0 g  (gravity on Z-axis)
```

### Step 2 — Verify Sensitivity Mode

The project uses **full resolution mode** (`DATA_FORMAT = 0x0B`, which sets the `FULL_RES` bit). In this mode, the ADXL345 automatically scales its output so that sensitivity is always **3.9 mg/LSB** regardless of the selected g-range:

| DATA_FORMAT (0x31) | Range | FULL_RES bit | Sensitivity |
|--------------------|-------|:------------:|-------------|
| `0x00` | ±2g  | 0 (off) | 3.9 mg/LSB |
| `0x01` | ±4g  | 0 (off) | 3.9 mg/LSB |
| `0x02` | ±8g  | 0 (off) | 3.9 mg/LSB |
| `0x03` | ±16g | 0 (off) | 3.9 mg/LSB |
| `0x0B` | ±16g | **1 (on)** | **3.9 mg/LSB** |

> ✅ **Current configuration:** `SENSITIVITY = 0.0039` is correct for full resolution mode (`0x0B`). The sensitivity stays constant at 3.9 mg/LSB in full resolution mode — only the measurable range changes.

### Step 3 — Tune the Conversion Factor

1. Run the machine at a **known RPM** (use a tachometer as ground truth).
2. Record the `Vibration` value output by the script.
3. Calculate:

```
conversion_factor = known_RPM / measured_vibration
```

4. Update `pro.py`:

```python
conversion_factor = <your_calculated_value>
```

### Step 4 — Verify Threshold

The default RPM threshold is `3000`. Adjust to match your machine's rated maximum:

```python
RPM_THRESHOLD = 3000  # Change to match your equipment's spec
```

---

## ▶️ Usage

### Running the Script

```bash
python3 pro.py
```

### What You'll See

**Console output** (printed every 0.1 seconds):

```
DateTime: 2024-01-15 14:32:01  Vibration: 0.843  Scaled RPM: 84.3
DateTime: 2024-01-15 14:32:01  Vibration: 1.205  Scaled RPM: 120.5
DateTime: 2024-01-15 14:32:01  Vibration: 2.971  Scaled RPM: 297.1
...
```

**Live Plot**: A dual-axis real-time chart:
- 🔴 **Red axis (left)** — RPM over time
- 🔵 **Blue axis (right)** — Vibration magnitude over time
- 🔴 **Dashed red line** — RPM threshold alert at 3,000 RPM

### Stopping the Script

Press `Ctrl + C` to stop gracefully:

```
Exiting the program.
```

---

## 📦 Data Collection

### Physical Setup

The ADXL345 sensor should be **rigidly mounted** to the machine frame or bearing housing using:
- Epoxy adhesive (permanent, best frequency response)
- Magnetic mount (temporary, good for testing)
- Screwed bracket (semi-permanent)

> 📌 **Tip:** Mount the sensor as close to the bearing or rotor as possible for the best signal-to-noise ratio.

### Data Collection Pipeline

```
Machine Vibration
       │
       ▼
  ADXL345 (I2C, 3-axis)
       │
       ▼
  RPi 4 reads 6 bytes per sample
       │
       ▼
  Converts raw → g values
       │
       ▼
  Computes RMS magnitude
       │
       ▼
  Maps to RPM estimate
       │
    ┌──┴──┐
    ▼      ▼
CSV File  Live Plot
```

### Eddy Current Separator Context

Eddy current separators use a high-speed rotating magnetic drum to separate non-ferrous metals from other materials. The rotor speed directly affects separation efficiency. This project enables:
- Non-invasive rotor RPM monitoring
- Early detection of rotor imbalance (abnormal vibration spikes)
- Correlation of RPM with material separation performance

---

## 📄 Output Format

### Console Output

```
DateTime: YYYY-MM-DD HH:MM:SS  Vibration: <float>  Scaled RPM: <float>
```

### CSV File (`rpm_data.csv`)

The file is written (overwritten) every loop iteration at `rpm_data.csv`:

```csv
DateTime,Time,RPM,Vibration
2024-01-15 14:32:01,1705326721.43,84.3,0.843
2024-01-15 14:32:01,1705326721.53,91.7,0.917
2024-01-15 14:32:02,1705326722.63,120.5,1.205
```

| Column | Type | Description |
|--------|------|-------------|
| `DateTime` | string | Human-readable timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `Time` | float | Unix epoch timestamp (seconds) |
| `RPM` | float | Estimated RPM (clamped to 0–3000) |
| `Vibration` | float | RMS vibration magnitude (g) |

> 💡 **Tip:** The CSV is **overwritten** each iteration with all accumulated data. To preserve individual sessions, rename the file after each run or modify the script to use append mode and session-based filenames.

---

## 🔧 Troubleshooting

### ❌ `OSError: [Errno 121] Remote I/O error`

**Cause:** I2C communication failure — sensor not found or wiring issue.

**Fix:**
1. Check all wiring connections (SDA → Pin 3, SCL → Pin 5).
2. Confirm I2C is enabled: `sudo raspi-config → Interface Options → I2C`.
3. Verify sensor address: `i2cdetect -y 1` should show `0x53`.
4. Ensure VCC is connected to 3.3V, **not** 5V.

---

### ❌ `ModuleNotFoundError: No module named 'smbus'`

**Fix:**

```bash
sudo apt-get install python3-smbus -y
# OR
pip3 install smbus2
```

If using `smbus2`, update the import in `pro.py`:

```python
import smbus2 as smbus
```

---

### ❌ All vibration values are near zero

**Cause:** Sensor in standby mode or not initialized correctly.

**Fix:** Confirm the POWER_CTL register write succeeds. Add a debug read:

```python
power_ctl = bus.read_byte_data(ACCELEROMETER_ADDR, 0x2D)
print(f"POWER_CTL: {hex(power_ctl)}")  # Should print 0x8
```

---

### ❌ RPM values seem unrealistically high or low

**Cause:** The `conversion_factor` is not calibrated for your machine.

**Fix:** Recalibrate using a tachometer (see [Calibration](#-calibration) section).

---

### ❌ Live plot is slow or freezing

**Cause:** Matplotlib's interactive mode can be slow with many data points.

**Fix:** Limit the plot window to the last N samples:

```python
# Keep only last 200 samples in plot
ax1.plot(time_data[-200:], rpm_data[-200:], color='tab:red')
ax2.plot(time_data[-200:], vibration_data[-200:], color='tab:blue')
```

---

### ❌ `FileNotFoundError` when saving CSV

**Cause:** Script doesn't have write permissions to current directory.

**Fix:** Run from the project directory or specify an absolute path:

```python
with open('/home/pi/Vibration-to-Rpm/rpm_data.csv', mode='w', newline='') as file:
```

---

## 📊 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Sampling Rate** | ~10 Hz | Limited by 0.1s loop sleep |
| **ADXL345 Max ODR** | 3,200 Hz | Hardware capability |
| **I2C Speed** | 400 kHz (fast mode) | RPi I2C default |
| **Measurement Range** | 0 – 3,000 RPM | Software clamped |
| **Sensitivity** | 0.0039 g/LSB | At ±16g range |
| **Resolution** | 13-bit | ADXL345 full resolution mode |
| **RPM Precision** | ±5–10% | Depends on calibration |
| **Latency** | < 200 ms | Loop + I2C overhead |
| **CSV Write Interval** | 0.1 s | Every loop iteration |

> 📌 For higher sampling rates, consider disabling matplotlib's real-time rendering during data collection and plotting offline.

---

## 🚀 Future Improvements

### 1. FFT-Based Frequency Analysis

Replace the linear vibration-to-RPM formula with a proper **Fast Fourier Transform** to extract the dominant frequency from the vibration signal:

```python
from scipy.fft import fft, fftfreq
import numpy as np

def vibration_to_rpm_fft(samples, sample_rate):
    N = len(samples)
    yf = np.abs(fft(samples))
    xf = fftfreq(N, 1 / sample_rate)
    dominant_freq = xf[np.argmax(yf[:N//2])]  # Hz
    rpm = dominant_freq * 60                   # Hz → RPM
    return rpm
```

### 2. Higher Sampling Rate

Leverage ADXL345's FIFO buffer (32 samples deep) for burst reads at up to 800 Hz:

```python
# Set output data rate to 800 Hz (register 0x2C, BW_RATE)
bus.write_byte_data(ACCELEROMETER_ADDR, 0x2C, 0x0D)
```

### 3. Machine Learning Anomaly Detection

Train a model on baseline vibration signatures to detect:
- Bearing wear
- Rotor imbalance
- Misalignment

Suggested libraries: `scikit-learn` (Isolation Forest), `TensorFlow` (LSTM autoencoder).

### 4. Wireless Data Streaming

Replace the local CSV with MQTT or HTTP streaming for remote monitoring:

```python
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect("broker.local", 1883)
client.publish("vibration/rpm", payload=str(scaled_rpm))
```

### 5. Web Dashboard

Build a live web dashboard using Flask + Chart.js or Grafana + InfluxDB to visualize vibration trends over time.

### 6. Alert System

Send email/SMS alerts when RPM exceeds the threshold:

```python
import smtplib
if scaled_rpm > RPM_THRESHOLD:
    # send alert email
```

### 7. Multi-Sensor Support

Add support for multiple ADXL345 sensors at different mounting points using the alternate I2C address `0x1D` (SDO → 3.3V).

---

## 📚 References

### Sensor Datasheets

- [ADXL345 Datasheet — Analog Devices](https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf)
- [LM393 Comparator Datasheet — Texas Instruments](https://www.ti.com/lit/ds/symlink/lm393.pdf)
- [Raspberry Pi 4 Hardware Documentation](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html)

### Signal Processing

- [NumPy FFT Documentation](https://numpy.org/doc/stable/reference/routines.fft.html)
- [SciPy Signal Processing](https://docs.scipy.org/doc/scipy/reference/signal.html)
- *The Scientist and Engineer's Guide to Digital Signal Processing* — Steven W. Smith ([free online](https://www.dspguide.com/))

### I2C & Raspberry Pi

- [RPi I2C Setup Guide](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)
- [smbus2 Python Library](https://pypi.org/project/smbus2/)
- [ADXL345 with Raspberry Pi Tutorial — Adafruit](https://learn.adafruit.com/adxl345-digital-accelerometer)

### Vibration Analysis

- [ISO 10816 — Mechanical vibration evaluation standard](https://www.iso.org/standard/50450.html)
- [Vibration Analysis for Predictive Maintenance — SKF](https://www.skf.com/group/industries/maintenance)

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/fft-analysis`
3. Commit your changes: `git commit -m 'Add FFT-based RPM calculation'`
4. Push to the branch: `git push origin feature/fft-analysis`
5. Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/DawodRhman">DawodRhman</a> &nbsp;|&nbsp;
  ⭐ Star this repo if you found it useful!
</p>
