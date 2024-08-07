---

# CCTV Monitoring with YOLOv8

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is a sophisticated CCTV monitoring application designed to detect and count objects such as cars, motorcycles, and people using the cutting-edge YOLOv8 model. The application supports multiple CCTV camera feeds via RTSP, making it ideal for real-time monitoring and analysis in urban environments, traffic management, and security systems.

## Features

- **Real-Time Object Detection:** Leverages YOLOv8 for quick and precise object detection.

- **Multi-Camera Integration:** Handles multiple RTSP streams, allowing concurrent monitoring from various locations.

- **Object Counting:** Efficiently counts objects like cars, motorcycles, and people, providing valuable data for traffic and security applications.

- **User-Friendly Interface:** Easy-to-use interface for configuring detection parameters and viewing results in real-time.

- **GPU Acceleration:** Optimized for high performance using GPU, ensuring smooth processing of high-resolution video streams.

- **Scalability:** Suitable for large-scale deployments with the ability to handle multiple camera feeds.

## Installation

To set up the application, follow these instructions:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Arifmaulanaazis/CCTV-Monitoring.git
   cd CCTV-Monitoring
   ```

2. **Install dependencies:**

   Ensure you have Python 3.8+ and a CUDA-capable GPU. Then, install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure RTSP streams:**

   You will need to create and edit the `urls.json` file to specify your camera sources. This file should contain location names as keys and a list of camera URLs or indices as values. Here's an example format:

   ```json
   {
       "Location 1": [
           "rtsp://username:password@ip_address:port/path"
       ],
       "Location 2": [
           "http://streaming_address:port/path",
           "1"  // This can be a local camera index (e.g., 0, 1, 2) for USB webcams
       ],
       ...
   }
   ```

   **Note:** The `urls.json` file can contain various camera sources, such as:
   - **RTSP URLs:** For IP cameras.
   - **HTTP/HTTPS Streaming URLs:** For web streams.
   - **Local Camera Indices:** Using numbers like `0`, `1`, `2`, etc., to reference built-in or USB webcams connected to your machine.

4. **Run the application:**

   Start the application with the following command:

   ```bash
   python GUI.py
   ```

## Usage

- **Monitoring:** View live detection results and object counts directly through the application's interface.

- **Data Analysis:** Export detection data for further analysis or integration with other systems.

## Applications

- **Traffic Monitoring:** Analyze traffic patterns, vehicle counts, and congestion levels in real-time.

- **Security Surveillance:** Enhance security by detecting and counting people and vehicles in restricted areas.

- **Urban Planning:** Gather valuable data for city planning and infrastructure development.

## Contributions

Contributions are welcome! Please feel free to submit issues, pull requests, or suggest enhancements.

## License

This project is licensed under the MIT License.

---
