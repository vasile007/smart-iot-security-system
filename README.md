# Smart IoT Security System

A Raspberry Pi 5 based security system developed in Python.

## Features

- PIN-protected control panel
- Vibration detection
- Buzzer alarm
- Camera image capture
- Live camera monitoring
- Email alerts with photo attachments
- Security event logging
- Temporary lockout after multiple incorrect PIN attempts

## Technologies

- Python
- Tkinter
- Raspberry Pi 5
- RPi.GPIO
- Raspberry Pi Camera Module 3
- SMTP / Gmail
- SW-420 vibration sensor
- PIR motion sensor
- Active buzzer

## Hardware

- Raspberry Pi 5
- SW-420 vibration sensor
- PIR motion sensor
- Raspberry Pi Camera Module 3
- Active buzzer
- Jumper wires
- MicroSD card

## Demo

YouTube demo:

https://youtube.comhorts/TapgNVIfKLA

## Configuration

Create environment variables for email alerts:

```env
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECEIVER=your_email@gmail.com

See .env.example for an example configuration.

Security

Sensitive credentials are not included in the repository.

Future Improvements
Cloud storage for captured images
Mobile remote monitoring
Facial recognition
Improved motion detection
Encrypted communication
Multi-factor authentication


