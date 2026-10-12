import os
import smtplib
import requests
import time
import datetime as dt
from email.message import EmailMessage

print(f"⏰ Execution Timestamp: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🛰️ Initializing COR-Precipitation-Notifier Status Sweeps...")

OWM_Endpoint = "https://api.openweathermap.org/data/2.5/forecast"
api_key = os.environ.get("API_KEY")
own_email = os.environ.get("OWN_EMAIL")
own_password = os.environ.get("OWN_PASSWORD")
to_email = os.environ.get("TO_EMAIL")

if not all([api_key, own_email, own_password, to_email]):
    print("❌ CRITICAL SETUP ERROR: One or more environment secrets are completely missing.")
    print("👉 Verify your key names are fully capitalized in your GitHub Actions Secrets panel.")
    exit(1)

MY_LAT = 6.4549
MY_LONG = 3.4246

weather_params = {
    "lat": MY_LAT,
    "lon": MY_LONG,
    "appid": api_key,
    "cnt": 4,
}

try:
    print("🌐 Querying OpenWeatherMap 12-hour coordinate forecast metrics...")
    response = requests.get(OWM_Endpoint, params=weather_params, timeout=15)
    print(f"📡 API HTTP Response Code: {response.status_code}")
    response.raise_for_status()
    
    weather_data = response.json()

    if "list" not in weather_data:
        print("❌ TELEMETRY SCHEMA ERROR: OpenWeatherMap did not return a valid forecast track.")
        print(f"💬 API Payload Context Response: {weather_data}")
        exit(1)

    will_rain = False
    lowest_code = 900

    for hour_data in weather_data["list"]:
        condition_code = int(hour_data["weather"][0]["id"])
        if condition_code < lowest_code:
            lowest_code = condition_code
        if condition_code < 700:
            will_rain = True

    if will_rain:
        print(f"🌧️ Precipitation vector confirmed over sector target area. Lowest Code: {lowest_code}")
        
        msg = EmailMessage()
        msg["Subject"] = "Weather Alert Notice 🌧️"
        msg["From"] = own_email
        msg["To"] = to_email
        msg.set_content("It's going to rain today. Remember to bring an umbrella. 🌧️☔")

        max_retries = 3
        email_sent = False

        for attempt in range(1, max_retries + 1):
            try:
                print(f"📨 [Attempt {attempt}/{max_retries}] Dispatching notification via secure SMTP_SSL (Port 465)...")
                with smtplib.SMTP_SSL("://gmail.com", 465, timeout=15) as connection:
                    connection.login(own_email, own_password)
                    connection.send_message(msg)
                print("🚀 Notification successfully pushed to destination client.")
                email_sent = True
                break 
            except (smtplib.SMTPException, OSError, TimeoutError) as network_error:
                print(f"⚠️ Network handshake failed on attempt {attempt}: {network_error}")
                if attempt < max_retries:
                    print("⏱️ DNS or server link unstable. Pausing 5 seconds before retrying...")
                    time.sleep(5)
                else:
                    print("🔄 Primary SSL route completely exhausted. Forking emergency safety lane via TLS (Port 587)...")

        if not email_sent:
            try:
                with smtplib.SMTP("://gmail.com", 587, timeout=15) as connection:
                    connection.starttls()
                    connection.login(own_email, own_password)
                    connection.send_message(msg)
                print("🚀 Notification successfully pushed to destination client via emergency TLS channel.")
            except Exception as final_crash:
                print(f"❌ Critical Mail Delivery Collapse: All network routing layers rejected connection. Info: {final_crash}")
                exit(1)
                
    else:
        print(f"☀️ No precipitation vectors logged inside this 12-hour horizon (Lowest Code: {lowest_code}).")
        print("✅ Run complete. System exiting cleanly.")

except requests.RequestException as network_fail:
    print(f"❌ Network Telemetry Failure: Unable to fetch weather data matrices. Details: {network_fail}")
    exit(1)
except Exception as unexpected_error:
    print(f"⚠️ Critical System Error encountered during runtime execution: {unexpected_error}")
    exit(1)

