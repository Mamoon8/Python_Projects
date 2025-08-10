#Week 5 Project Alarm Clock using API and moduels
"""
This is an advanced topic so if you struggle use this as a guide or a reference
"""
import time
import requests

def get_current_time():
    response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC")
    if response.status_code == 200:
        data = response.json()
        return data["datetime"]
    return None

def set_alarm(alarm_time):
    while True:
        current_time = get_current_time()
        if current_time and current_time >= alarm_time:
            print("Alarm ringing!")
            break
        time.sleep(1)

def stop_alarm():
    print("Alarm stopped.")

def snooze_alarm():
    print("Alarm snoozed for 5 minutes.")
    time.sleep(300)

def main():
    print("Welcome to the Alarm Clock!")
    alarm_time = input("Enter the alarm time (YYYY-MM-DDTHH:MM:SS): ")
    set_alarm(alarm_time)
    while alarm_time:
        command = input("Enter 'stop' to stop the alarm or 'snooze' to snooze it: ")
        if command == "stop":
            stop_alarm()
            break
        elif command == "snooze":
            snooze_alarm()

