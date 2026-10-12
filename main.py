import os
import requests
import datetime as dt

print(f"⏰ Execution Timestamp: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("🛰️ Initializing COR-Precipitation-Notifier Workspace...")

OWM_Endpoint = "https://api.openweathermap.org/data/2.5/forecast"
api_key = os.environ.get("API_KEY")
discord_webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")

if not api_key or not discord_webhook_url:
    print("❌ CRITICAL SETUP ERROR: One or more required environment variables are completely missing.")
    print("👉 Verify your key names are capitalized in your GitHub Actions Secrets panel.")
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
        
        payload = {
            "content": f"⚠️ **WEATHER ALERT:** It is going to rain today over your coordinate matrix sector! Remember to bring an umbrella. 🌧️☔\n*(Lowest Weather Code logged: **{lowest_code}**)*"
        }

        print("📨 Dispatching webhook payload to Discord channel over HTTPS (Port 443)...")
        webhook_response = requests.post(discord_webhook_url, json=payload, timeout=15)
        
        if webhook_response.status_code in:
            print("🚀 Notification successfully pushed to Discord client canvas!")
        else:
            print(f"❌ Webhook communication failed with status: {webhook_response.status_code}")
            exit(1)
            
    else:
        print(f"☀️ No precipitation vectors logged inside this 12-hour horizon (Lowest Code: {lowest_code}).")
        print("✅ Run complete. System exiting cleanly.")

except requests.RequestException as network_fail:
    print(f"❌ Network Telemetry Failure: Details: {network_fail}")
    exit(1)
except Exception as unexpected_error:
    print(f"⚠️ Critical System Error encountered: {unexpected_error}")
    exit(1)

