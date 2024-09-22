import smbus
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import csv

# Define the I2C address for the accelerometer
ACCELEROMETER_ADDR = 0x53

# Register addresses for accelerometer data
ACCELEROMETER_DATA_REG = 0x32

# Sensitivity value for the accelerometer (in g per LSB)
SENSITIVITY = 0.0039  # Adjust as per your accelerometer specifications

# RPM threshold for the red line
RPM_THRESHOLD = 3000

# Create an instance of the smbus object
bus = smbus.SMBus(1)  # Use 1 for RPi 3, 4; 0 for RPi 1, 2

def initialize_accelerometer(addr):
    # POWER_CTL Register (0x2D)
    # Bit 3 (0-based index) sets the measure bit, activating the accelerometer
    bus.write_byte_data(addr, 0x2D, 0x08)

    # DATA_FORMAT Register (0x31)
    # Set the range to +/- 16g (bits 3 and 2)
    bus.write_byte_data(addr, 0x31, 0x0B)

def read_accelerometer_data(addr, data_reg):
    # Read the accelerometer data (assume 6 bytes for X, Y, Z)
    data = bus.read_i2c_block_data(addr, data_reg, 6)
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]
    return x * SENSITIVITY, y * SENSITIVITY, z * SENSITIVITY

def calculate_vibration(x, y, z):
    # Calculate the root mean square (RMS) of the accelerometer readings to represent vibration
    rms = np.sqrt(x**2 + y**2 + z**2)
    return rms

def vibration_to_rpm(vibration):
    # Assuming a linear relationship between vibration and RPM
    # You may need to calibrate this relationship based on your specific setup
    conversion_factor = 100  # Adjust as needed
    rpm = conversion_factor * vibration
    return rpm

try:
    initialize_accelerometer(ACCELEROMETER_ADDR)

    # Lists to store data for plotting
    time_data = []
    vibration_data = []
    rpm_data = []

    plt.ion()  # Enable interactive mode for live plotting

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('RPM', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('Vibration', color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    while True:
        current_time = time.time()
        date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        accelerometer_data = read_accelerometer_data(ACCELEROMETER_ADDR, ACCELEROMETER_DATA_REG)

        # Calculate vibration from the accelerometer values
        avg_vibration = calculate_vibration(accelerometer_data[0], accelerometer_data[1], accelerometer_data[2])

        # Convert vibration to RPM
        avg_rpm = vibration_to_rpm(avg_vibration)

        # Scale RPM between 0 and 3000 RPM
        scaled_rpm = min(max(avg_rpm, 0), RPM_THRESHOLD)

        # Store data for plotting
        time_data.append(current_time)  # Use time as x-axis
        vibration_data.append(avg_vibration)
        rpm_data.append(scaled_rpm)

        # Plot RPM and vibration on the same graph with real-time date and time
        ax1.plot(time_data, rpm_data, color='tab:red', label='RPM')
        ax2.plot(time_data, vibration_data, color='tab:blue', label='Vibration')

        # Add a red line when RPM exceeds the threshold
        if scaled_rpm > RPM_THRESHOLD:
            ax1.axhline(y=RPM_THRESHOLD, color='red', linestyle='--', label='Threshold (3000 RPM)')

        fig.tight_layout()
        plt.draw()
        plt.pause(0.1)  # Adjust the pause duration as needed

        print("DateTime:", date_time, "Vibration:", avg_vibration, "Scaled RPM:", scaled_rpm)

        # Save data to CSV file
        with open('rpm_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['DateTime', 'Time', 'RPM', 'Vibration'])
            writer.writerows(zip([date_time]*len(time_data), time_data, rpm_data, vibration_data))

        time.sleep(0.1)  # Adjust the sleep duration as needed

except KeyboardInterrupt:
    print("Exiting the program.")
