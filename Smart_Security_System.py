import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import os
import subprocess
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ============================================================
# SMART SECURITY CONTROL PANEL
# Raspberry Pi Security System
# Features:
# - PIN protected control panel
# - Vibration sensor detection
# - Buzzer alarm
# - Camera capture
# - Live camera preview
# - Email alerts with photo attachment
# - Security event log
# ============================================================

# =========================
# HARDWARE PINS
# =========================
VIBRATION = 27
PIR = 17
BUZZER = 18

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(VIBRATION, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(PIR, GPIO.IN)  # PIR connected, but disabled in alarm logic because of false triggers
GPIO.setup(BUZZER, GPIO.OUT, initial=GPIO.HIGH)  # Active LOW buzzer: LOW = ON, HIGH = OFF

# =========================
# SYSTEM SETTINGS
# =========================
PIN_CODE = "1234"

# Gmail App Password settings
# IMPORTANT: use Gmail App Password, not your normal Gmail password
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

armed = False
alarm_active = False
show_pin = False
unlocked = False
lockout_active = False

failed_attempts = 0
MAX_ATTEMPTS = 3

last_photo = None
camera_process = None

PHOTO_FOLDER = "security_photos"

if not os.path.exists(PHOTO_FOLDER):
    os.makedirs(PHOTO_FOLDER)

# =========================
# COLORS / UI STYLE
# =========================
BG_DARK = "#0f1117"
CARD = "#1b1f2a"
CARD_2 = "#242a38"
TEXT = "#f5f6fa"
MUTED = "#9aa4b2"

BLUE = "#3498db"
GREEN = "#2ecc71"
RED = "#e74c3c"
YELLOW = "#f1c40f"
ORANGE = "#e67e22"
PURPLE = "#9b59b6"

current_status_color = BLUE

# =========================
# LOG FUNCTION
# =========================
def log_event(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("security_log.txt", "a") as file:
        file.write(f"{timestamp} - {event}\n")

    # Show event inside GUI log if GUI is ready
    try:
        event_log.insert(tk.END, f"{timestamp}  |  {event}\n")
        event_log.see(tk.END)
    except Exception:
        pass

# =========================
# EMAIL FUNCTION
# =========================
def send_email_alert(subject, body, attachment_path=None):
    try:
        if "CHANGE_HERE" in EMAIL_SENDER or "CHANGE_HERE" in EMAIL_PASSWORD or "CHANGE_HERE" in EMAIL_RECEIVER:
            log_event("Email not sent - email settings not configured")
            return

        msg = EmailMessage()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.set_content(body)

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)

            msg.add_attachment(
                file_data,
                maintype="image",
                subtype="jpeg",
                filename=file_name
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)

        log_event("Email alert sent successfully")

    except Exception as e:
        log_event(f"Email error: {e}")
        print("Email error:", e)

# =========================
# GUI STATUS
# =========================
def set_status(text, color, subtitle=""):
    global current_status_color
    current_status_color = color

    status_badge.config(text=text, bg=color)
    main_status.config(text=text, fg=color)
    status_subtitle.config(text=subtitle)
    root.configure(bg=BG_DARK)

def set_card(label, value, color):
    label.config(text=value, fg=color)

def update_dashboard(system_value=None, sensor_value=None, camera_value=None, email_value=None):
    if system_value is not None:
        system_state_value.config(text=system_value)

    if sensor_value is not None:
        sensor_state_value.config(text=sensor_value)

    if camera_value is not None:
        camera_state_value.config(text=camera_value)

    if email_value is not None:
        email_state_value.config(text=email_value)

# =========================
# CAMERA FUNCTIONS
# =========================
def capture_photo(force=False):
    global last_photo

    if not unlocked and not force:
        set_status(
            "PIN REQUIRED",
            RED,
            "Unlock the control panel before using the camera."
        )
        return None

    try:
        filename = datetime.now().strftime("capture_%Y-%m-%d_%H-%M-%S.jpg")
        filepath = os.path.join(PHOTO_FOLDER, filename)

        camera_status.config(text="Capturing photo...")
        update_dashboard(camera_value="CAPTURING")
        root.update()

        subprocess.run(
            [
                "rpicam-still",
                "-o", filepath,
                "-t", "1000",
                "--width", "640",
                "--height", "480"
            ],
            check=True
        )

        last_photo = filepath
        camera_status.config(text=f"Last capture: {filename}")
        update_dashboard(camera_value="READY")
        log_event(f"Photo captured: {filename}")

        return filepath

    except Exception as e:
        camera_status.config(text="Camera error")
        update_dashboard(camera_value="ERROR")
        log_event(f"Camera error: {e}")
        print("Camera error:", e)
        return None

def open_last_photo():
    if not unlocked:
        set_status("PIN REQUIRED", RED, "Unlock the control panel before opening photos.")
        return

    if last_photo:
        subprocess.Popen(["xdg-open", last_photo])
        log_event("Last photo opened")
    else:
        camera_status.config(text="No photo captured yet")

def open_live_camera():
    global camera_process

    if not unlocked:
        set_status("PIN REQUIRED", RED, "Unlock the control panel before opening live camera.")
        return

    if camera_process is None:
        camera_process = subprocess.Popen(
            [
                "rpicam-hello",
                "-t", "0",
                "--fullscreen", "0",
                "--preview", "100,100,640,480"
            ]
        )
        camera_status.config(text="Live camera opened")
        update_dashboard(camera_value="LIVE")
        log_event("Live camera opened")
    else:
        camera_status.config(text="Live camera already open")

def close_live_camera():
    global camera_process

    if not unlocked:
        set_status("PIN REQUIRED", RED, "Unlock the control panel before closing live camera.")
        return

    if camera_process is not None:
        camera_process.terminate()
        camera_process = None
        camera_status.config(text="Live camera closed")
        update_dashboard(camera_value="READY")
        log_event("Live camera closed")
    else:
        camera_status.config(text="Live camera is not open")

# =========================
# BUZZER FUNCTIONS
# =========================
def buzzer_on():
    GPIO.output(BUZZER, GPIO.LOW)

def buzzer_off():
    GPIO.output(BUZZER, GPIO.HIGH)

def beep_alarm():
    # Fast alert sound
    for i in range(20):
        buzzer_on()
        root.update()
        root.after(80)

        buzzer_off()
        root.update()
        root.after(80)

def beep_countdown():
    buzzer_on()
    root.update()
    root.after(150)
    buzzer_off()

# =========================
# PIN / SECURITY FUNCTIONS
# =========================
def toggle_pin():
    global show_pin
    show_pin = not show_pin

    if show_pin:
        pin_entry.config(show="")
        show_btn.config(text="HIDE PIN")
    else:
        pin_entry.config(show="*")
        show_btn.config(text="SHOW PIN")

def start_lockout(seconds):
    global lockout_active, unlocked

    lockout_active = True
    unlocked = False

    set_status(
        "SECURITY LOCKOUT",
        RED,
        f"Too many wrong PIN attempts. Wait {seconds} seconds."
    )
    update_dashboard(system_value="LOCKOUT")

    log_event("Security lockout activated")

    if seconds > 0:
        root.after(1000, lambda: continue_lockout(seconds - 1))
    else:
        end_lockout()

def continue_lockout(seconds):
    if seconds > 0:
        set_status(
            "SECURITY LOCKOUT",
            RED,
            f"Too many wrong PIN attempts. Wait {seconds} seconds."
        )
        root.after(1000, lambda: continue_lockout(seconds - 1))
    else:
        end_lockout()

def end_lockout():
    global lockout_active, failed_attempts

    lockout_active = False
    failed_attempts = 0

    set_status("SYSTEM DISARMED", BLUE, "Lockout ended. Enter PIN to unlock.")
    update_dashboard(system_value="DISARMED")
    log_event("Security lockout ended")

def wrong_pin():
    global failed_attempts

    if lockout_active:
        return

    failed_attempts += 1

    set_status(
        "ACCESS DENIED",
        RED,
        f"Wrong PIN entered ({failed_attempts}/{MAX_ATTEMPTS})."
    )

    log_event(f"Wrong PIN entered ({failed_attempts}/{MAX_ATTEMPTS})")

    if failed_attempts >= MAX_ATTEMPTS:
        log_event("Unauthorized access attempt - 3 wrong PINs")

        photo = capture_photo(force=True)

        send_email_alert(
            "Security Alert - Too Many Wrong PIN Attempts",
            "Warning: The wrong PIN was entered 3 times. Security lockout has been activated.",
            photo
        )

        beep_alarm()
        start_lockout(30)

def unlock_system():
    global unlocked, failed_attempts

    if lockout_active:
        return

    pin = pin_entry.get()

    if pin == PIN_CODE:
        unlocked = True
        failed_attempts = 0
        pin_entry.delete(0, tk.END)

        set_status("ACCESS GRANTED", GREEN, "Control panel unlocked.")
        update_dashboard(system_value="UNLOCKED")
        log_event("Control panel unlocked")
    else:
        pin_entry.delete(0, tk.END)
        wrong_pin()

def require_access():
    if lockout_active:
        set_status("SECURITY LOCKOUT", RED, "Please wait until lockout ends.")
        return False

    if not unlocked:
        set_status("PIN REQUIRED", RED, "Enter PIN and unlock the control panel first.")
        return False

    return True

# =========================
# ARM / DISARM
# =========================
def arm_countdown(seconds):
    global armed, alarm_active

    if seconds > 0:
        set_status(
            f"ARMING IN {seconds}",
            YELLOW,
            "Please leave the secured area."
        )
        update_dashboard(system_value="ARMING")
        beep_countdown()
        root.after(1000, lambda: arm_countdown(seconds - 1))

    else:
        armed = True
        alarm_active = False

        set_status(
            "SYSTEM ARMED",
            GREEN,
            "Vibration sensor is now monitoring the secured area."
        )

        update_dashboard(system_value="ARMED", sensor_value="MONITORING")
        log_event("System armed")

def arm_system():
    if not require_access():
        return

    log_event("Arming started")
    arm_countdown(5)

def disarm_system():
    global armed, alarm_active, unlocked

    if not require_access():
        return

    armed = False
    alarm_active = False
    unlocked = False

    buzzer_off()

    set_status(
        "SYSTEM DISARMED",
        BLUE,
        "Security system is off. Control panel locked."
    )

    update_dashboard(system_value="DISARMED", sensor_value="STANDBY")
    log_event("System disarmed and panel locked")

# =========================
# ALARM
# =========================
def trigger_alarm(reason):
    global alarm_active

    if not alarm_active:
        alarm_active = True

        set_status(
            "SECURITY BREACH",
            RED,
            f"Threat level: HIGH | {reason}"
        )

        update_dashboard(system_value="ALERT", sensor_value="TRIGGERED")
        log_event(f"ALARM: {reason}")

        photo = capture_photo(force=True)

        send_email_alert(
            "Security Alert - Sensor Triggered",
            f"Warning: {reason}. The security system detected activity.",
            photo
        )

        beep_alarm()

def check_alert():
    global alarm_active

    buzzer_off()

    if not require_access():
        return

    if armed:
        alarm_active = False

        set_status(
            "SYSTEM ARMED",
            GREEN,
            "Alert checked. Monitoring has resumed."
        )

        update_dashboard(system_value="ARMED", sensor_value="MONITORING")
        log_event("Alert acknowledged")

# =========================
# CHECK SENSORS
# =========================
def check_sensors():
    if armed and not alarm_active:
        if GPIO.input(VIBRATION) == 1:
            trigger_alarm("Vibration detected")

        # PIR / motion sensor disabled because it gives false triggers.
        # It remains connected for testing and future improvement.
        # if GPIO.input(PIR) == 1:
        #     trigger_alarm("Motion detected")

    root.after(300, check_sensors)

# =========================
# CLOSE APP
# =========================
def close_app():
    global camera_process

    if camera_process is not None:
        camera_process.terminate()
        camera_process = None

    buzzer_off()
    GPIO.cleanup()
    root.destroy()

# =========================
# BUTTON STYLE HELPERS
# =========================
def make_button(parent, text, command, width=18):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        width=width,
        height=2,
        bg=CARD_2,
        fg=TEXT,
        activebackground=BLUE,
        activeforeground=TEXT,
        bd=0,
        cursor="hand2"
    )

def make_action_button(parent, text, command, color, width=18):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Arial", 11, "bold"),
        width=width,
        height=2,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        bd=0,
        cursor="hand2"
    )

# =========================
# GUI
# =========================
root = tk.Tk()
root.title("Smart Security Control Panel")
root.geometry("1200x760")
root.configure(bg=BG_DARK)

# Header
header = tk.Frame(root, bg=BG_DARK)
header.pack(fill="x", padx=28, pady=(20, 10))

title = tk.Label(
    header,
    text="SMART SECURITY CONTROL PANEL",
    font=("Arial", 27, "bold"),
    bg=BG_DARK,
    fg=TEXT
)
title.pack(side="left")

status_badge = tk.Label(
    header,
    text="SYSTEM DISARMED",
    font=("Arial", 11, "bold"),
    bg=BLUE,
    fg="white",
    padx=18,
    pady=8
)
status_badge.pack(side="right")

# Main layout
main_layout = tk.Frame(root, bg=BG_DARK)
main_layout.pack(fill="both", expand=True, padx=28, pady=10)

left_panel = tk.Frame(main_layout, bg=CARD, width=760)
left_panel.pack(side="left", fill="both", expand=True, padx=(0, 12))

right_panel = tk.Frame(main_layout, bg=CARD, width=360)
right_panel.pack(side="right", fill="y", padx=(12, 0))

# Main status area
main_status = tk.Label(
    left_panel,
    text="SYSTEM DISARMED",
    font=("Arial", 38, "bold"),
    bg=CARD,
    fg=BLUE
)
main_status.pack(pady=(28, 5))

status_subtitle = tk.Label(
    left_panel,
    text="Panel locked. Enter PIN to unlock control access.",
    font=("Arial", 14),
    bg=CARD,
    fg=MUTED
)
status_subtitle.pack(pady=(0, 18))

# Dashboard cards
dashboard = tk.Frame(left_panel, bg=CARD)
dashboard.pack(pady=8)

def dashboard_card(parent, title_text, value_text, color):
    frame = tk.Frame(parent, bg=CARD_2, width=160, height=90)
    frame.pack_propagate(False)

    label_title = tk.Label(
        frame,
        text=title_text,
        font=("Arial", 10, "bold"),
        bg=CARD_2,
        fg=MUTED
    )
    label_title.pack(pady=(14, 4))

    label_value = tk.Label(
        frame,
        text=value_text,
        font=("Arial", 14, "bold"),
        bg=CARD_2,
        fg=color
    )
    label_value.pack()

    return frame, label_value

system_card, system_state_value = dashboard_card(dashboard, "SYSTEM STATUS", "DISARMED", BLUE)
sensor_card, sensor_state_value = dashboard_card(dashboard, "SENSOR STATUS", "STANDBY", YELLOW)
camera_card, camera_state_value = dashboard_card(dashboard, "CAMERA", "READY", GREEN)
email_card, email_state_value = dashboard_card(dashboard, "EMAIL ALERTS", "ENABLED", PURPLE)

system_card.grid(row=0, column=0, padx=8, pady=8)
sensor_card.grid(row=0, column=1, padx=8, pady=8)
camera_card.grid(row=0, column=2, padx=8, pady=8)
email_card.grid(row=0, column=3, padx=8, pady=8)

# PIN area
pin_area = tk.Frame(left_panel, bg=CARD)
pin_area.pack(pady=(20, 10))

pin_label = tk.Label(
    pin_area,
    text="SECURITY PIN",
    font=("Arial", 12, "bold"),
    bg=CARD,
    fg=MUTED
)
pin_label.grid(row=0, column=0, columnspan=3, pady=(0, 8))

pin_entry = tk.Entry(
    pin_area,
    font=("Arial", 22),
    show="*",
    justify="center",
    width=14,
    bg=BG_DARK,
    fg=TEXT,
    insertbackground=TEXT,
    bd=0
)
pin_entry.grid(row=1, column=0, padx=8, ipady=8)

show_btn = make_button(pin_area, "SHOW PIN", toggle_pin, width=12)
show_btn.grid(row=1, column=1, padx=8)

unlock_btn = make_action_button(pin_area, "UNLOCK PANEL", unlock_system, BLUE, width=16)
unlock_btn.grid(row=1, column=2, padx=8)

# Action buttons
actions = tk.Frame(left_panel, bg=CARD)
actions.pack(pady=18)

arm_btn = make_action_button(actions, "ARM SYSTEM", arm_system, GREEN, width=18)
arm_btn.grid(row=0, column=0, padx=8)

disarm_btn = make_action_button(actions, "DISARM SYSTEM", disarm_system, ORANGE, width=18)
disarm_btn.grid(row=0, column=1, padx=8)

check_btn = make_action_button(actions, "CHECK ALERT", check_alert, RED, width=18)
check_btn.grid(row=0, column=2, padx=8)

# Camera area
camera_box = tk.Frame(left_panel, bg=CARD_2)
camera_box.pack(fill="x", padx=30, pady=20)

camera_title = tk.Label(
    camera_box,
    text="CAMERA SURVEILLANCE",
    font=("Arial", 13, "bold"),
    bg=CARD_2,
    fg=TEXT
)
camera_title.pack(pady=(14, 8))

camera_buttons = tk.Frame(camera_box, bg=CARD_2)
camera_buttons.pack(pady=6)

capture_btn = make_button(camera_buttons, "CAPTURE PHOTO", capture_photo, width=17)
capture_btn.grid(row=0, column=0, padx=6)

live_btn = make_button(camera_buttons, "OPEN LIVE CAMERA", open_live_camera, width=18)
live_btn.grid(row=0, column=1, padx=6)

close_live_btn = make_button(camera_buttons, "CLOSE LIVE CAMERA", close_live_camera, width=18)
close_live_btn.grid(row=0, column=2, padx=6)

open_photo_btn = make_button(camera_buttons, "OPEN LAST PHOTO", open_last_photo, width=17)
open_photo_btn.grid(row=0, column=3, padx=6)

camera_status = tk.Label(
    camera_box,
    text="Last capture: none",
    font=("Arial", 10),
    bg=CARD_2,
    fg=MUTED
)
camera_status.pack(pady=(6, 14))

# Right panel: event log and info
right_title = tk.Label(
    right_panel,
    text="SECURITY EVENT LOG",
    font=("Arial", 16, "bold"),
    bg=CARD,
    fg=TEXT
)
right_title.pack(pady=(22, 8))

event_log = tk.Text(
    right_panel,
    height=22,
    width=42,
    bg=BG_DARK,
    fg=TEXT,
    insertbackground=TEXT,
    font=("Consolas", 9),
    bd=0,
    wrap="word"
)
event_log.pack(padx=18, pady=10)

info_box = tk.Frame(right_panel, bg=CARD_2)
info_box.pack(fill="x", padx=18, pady=12)

info_title = tk.Label(
    info_box,
    text="SYSTEM FEATURES",
    font=("Arial", 12, "bold"),
    bg=CARD_2,
    fg=TEXT
)
info_title.pack(pady=(12, 5))

info_text = tk.Label(
    info_box,
    text="PIN Protected\nEmail Notifications\nVibration Detection\nAudible Alarm\nCamera Surveillance",
    font=("Arial", 10),
    bg=CARD_2,
    fg=MUTED,
    justify="left"
)
info_text.pack(pady=(0, 12))

# Footer
footer = tk.Label(
    root,
    text="PIN Protected | Email Notifications | Vibration Detection | Buzzer Alarm | Camera Surveillance",
    font=("Arial", 11),
    bg=BG_DARK,
    fg=MUTED
)
footer.pack(pady=(0, 14))

root.protocol("WM_DELETE_WINDOW", close_app)

log_event("Application started")
check_sensors()
root.mainloop()
