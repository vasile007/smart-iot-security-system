# 🔐 Smart IoT Security System

A Raspberry Pi 5 based IoT security system built with Python, combining real-time sensor monitoring, camera surveillance, access control, automated alerts and a graphical control panel.

The system is designed to detect suspicious physical activity, capture photographic evidence, trigger an audible alarm and automatically send an email notification containing the captured image.

---

## 🎥 Demo

A full demonstration of the system is available here:

**YouTube:**
https://youtube.com/shorts/TapgNVIfKLA

The demonstration includes:

* PIN authentication
* Control panel unlocking
* System arming and disarming
* Vibration detection
* Automatic image capture
* Email alert transmission
* Live camera monitoring
* Security event logging
* Alert acknowledgement
* Security lockout after repeated incorrect PIN attempts

  ## 📸 Project Screenshots

### Security Control Panel

Smart Security Control Panel

<img width="400" height="300" alt="Picture1" src="https://github.com/user-attachments/assets/5763ac93-eaba-4239-84db-a4e715c167c0" />


### Hardware Setup

![Raspberry Pi Hardware Setup](screenshots/hardware-setup.jpg)

### Email Security Alert

![Email Security Alert](screenshots/email-alert.png)

---

## 🚀 Key Features

### 🔑 PIN Protected Control Panel

The system includes a PIN-based authentication mechanism that prevents unauthorized users from accessing security controls.

After **3 incorrect PIN attempts**, the system:

* Detects an unauthorized access attempt
* Captures a photo
* Sends an email security alert
* Activates the buzzer
* Locks the control panel for 30 seconds

---

### 📳 Vibration Intrusion Detection

An **SW-420 vibration sensor** continuously monitors the protected area while the system is armed.

When vibration is detected:

1. The system enters a security breach state
2. A security event is written to the log
3. The Raspberry Pi camera automatically captures an image
4. An email notification is generated
5. The image is attached to the alert email
6. The buzzer alarm is activated

---

### 📷 Camera Surveillance

The Raspberry Pi Camera Module 3 supports:

* Automatic security-event photography
* Manual image capture
* Opening the latest captured image
* Live camera preview

Captured images are stored locally in the `security_photos/` directory.

---

### 📧 Automated Email Alerts

Security alerts can be sent through Gmail SMTP.

Notifications can be triggered by:

* Vibration detection
* Multiple incorrect PIN attempts

The system can automatically attach a captured security image to the notification.

Credentials are loaded using environment variables and are **not stored inside the source code**.

---

### 🔊 Audible Alarm

An active buzzer connected to the Raspberry Pi provides local audible alerts.

The buzzer is used during:

* Intrusion detection
* Unauthorized access attempts
* System arming countdown

---

### 🖥️ Graphical Security Dashboard

The system includes a Tkinter graphical user interface displaying:

* System status
* Sensor status
* Camera status
* Email alert status
* Security event log
* PIN authentication controls
* Arm / Disarm controls
* Camera controls
* Alert acknowledgement

---

## 🧠 System Architecture

```text
                 ┌──────────────────────┐
                 │    Raspberry Pi 5    │
                 │                      │
                 │   Python + Tkinter   │
                 └──────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
  SW-420 Sensor       Camera Module 3        Buzzer
    GPIO 27                CSI               GPIO 18
        │                   │                   │
        └──────────────┬────┴───────────────────┘
                       │
                       ▼
               Security Event Logic
                       │
            ┌──────────┼──────────┐
            │          │          │
            ▼          ▼          ▼
        Event Log   Photo      Alarm
                       │
                       ▼
                 Gmail SMTP
                       │
                       ▼
                 Email Alert
```

---

## 🔧 Hardware

| Component                    | Purpose                               | Connection |
| ---------------------------- | ------------------------------------- | ---------- |
| Raspberry Pi 5               | Main controller                       | —          |
| SW-420 Vibration Sensor      | Intrusion detection                   | GPIO 27    |
| PIR Motion Sensor            | Motion detection / future development | GPIO 17    |
| Active Buzzer                | Audible alarm                         | GPIO 18    |
| Raspberry Pi Camera Module 3 | Image capture and live surveillance   | CSI        |
| Jumper Wires                 | Hardware connections                  | GPIO       |
| MicroSD Card                 | Raspberry Pi OS and storage           | —          |

> The PIR sensor remains physically connected but is currently disabled in the alarm logic because testing produced occasional false-positive detections.

---

## 💻 Technology Stack

### Software

* Python
* Tkinter
* Raspberry Pi OS
* RPi.GPIO
* SMTP
* Python `EmailMessage`
* `subprocess`
* `datetime`

### Raspberry Pi Camera Tools

* `rpicam-still`
* `rpicam-hello`

### Hardware

* Raspberry Pi 5
* Raspberry Pi Camera Module 3
* SW-420 Vibration Sensor
* PIR Motion Sensor
* Active Buzzer

---

## 📁 Project Structure

```text
smart-iot-security-system/
│
├── Smart_Security_System.py
├── README.md
├── .gitignore
├── .env.example
│
├── screenshots/
│   ├── dashboard.png
│   ├── security-alert.png
│   └── hardware-setup.jpg
│
└── docs/
    └── project-report.pdf
```

Runtime-generated files such as captured security images should not be committed to the repository.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/vasile007/smart-iot-security-system.git
cd smart-iot-security-system
```

### 2. Install Raspberry Pi GPIO support

```bash
sudo apt update
sudo apt install python3-rpi.gpio
```

### 3. Check camera support

```bash
rpicam-hello
```

### 4. Configure email credentials

Set the following environment variables:

```bash
export EMAIL_SENDER="your_email@gmail.com"
export EMAIL_PASSWORD="your_gmail_app_password"
export EMAIL_RECEIVER="receiver@gmail.com"
```

The project also includes `.env.example` as a configuration reference.

> Do not commit real passwords or Gmail App Passwords to GitHub.

---

## ▶️ Running the Application

Run the application directly on a Raspberry Pi:

```bash
python3 Smart_Security_System.py
```

The security control panel will open through the Tkinter GUI.

---

## 🔌 GPIO Configuration

```python
VIBRATION = 27
PIR = 17
BUZZER = 18
```

The project uses BCM GPIO numbering.

---

## 🛡️ Security Flow

```text
System Armed
     │
     ▼
Sensor Monitoring
     │
     ▼
Vibration Detected
     │
     ├──► Security Event Logged
     │
     ├──► Camera Captures Image
     │
     ├──► Email Alert Sent
     │
     └──► Buzzer Activated
```

---

## 🔐 Unauthorized Access Protection

```text
Wrong PIN
   │
   ▼
Attempt Counter
   │
   ├── Attempt 1
   ├── Attempt 2
   └── Attempt 3
          │
          ▼
 Unauthorized Access
          │
     ┌────┼────┐
     ▼    ▼    ▼
  Photo  Email Buzzer
          │
          ▼
    30s Lockout
```

---

## 🧪 Testing

The system was tested across its major functional components.

| Test                   | Result |
| ---------------------- | ------ |
| PIN Authentication     | ✅ PASS |
| Unlock Panel           | ✅ PASS |
| Arm System             | ✅ PASS |
| Disarm System          | ✅ PASS |
| Vibration Detection    | ✅ PASS |
| Camera Capture         | ✅ PASS |
| Email Alert            | ✅ PASS |
| Live Camera Monitoring | ✅ PASS |
| Event Logging          | ✅ PASS |
| Alert Acknowledgement  | ✅ PASS |

Testing also included repeated vibration events, camera capture, email notification delivery and system stability.

The PIR motion sensor was tested but produced occasional false-positive detections. For reliability, PIR monitoring was disabled in the final alarm logic while keeping the hardware available for future calibration.

---

## 📊 Example Security Event Flow

```text
Application started
Control panel unlocked
Arming started
System armed
ALARM: Vibration detected
Photo captured
Email alert sent successfully
Alert acknowledged
System disarmed
```

---

## 🧩 Technical Challenges

During development several practical IoT challenges were encountered:

* Integrating GPIO sensors with a graphical interface
* Coordinating camera capture with security events
* Managing false-positive PIR detections
* Sending image attachments through SMTP
* Maintaining system responsiveness while activating the buzzer
* Implementing secure PIN access and temporary lockout
* Managing live camera processes from Python

---

## 🔮 Future Improvements

Possible future improvements include:

* AWS or cloud storage for captured images
* Remote monitoring through a web or mobile application
* Facial recognition
* Improved PIR filtering and calibration
* Push notifications
* Encrypted communication
* Multi-factor authentication
* Cloud-based security event logging
* Remote system arming and disarming
* Containerised backend services for remote monitoring

---

## 📚 What This Project Demonstrates

This project demonstrates practical experience with:

* Internet of Things development
* Python programming
* Raspberry Pi development
* GPIO hardware integration
* Sensors and actuators
* Camera integration
* Event-driven security systems
* SMTP integration
* Authentication and access control
* GUI development
* Hardware troubleshooting
* System testing
* Reliability engineering

---

## 👤 Author

**Vasile Bejan**

GitHub: [vasile007](https://github.com/vasile007)

---

## ⚠️ Disclaimer

This project was developed for educational and portfolio purposes.

It is a prototype IoT security system and should not be considered a replacement for a professionally certified security or alarm system.
