import os
import smtplib
import requests

OWM_Endpoint = "https://api.openweathermap.org/data/2.5/forecast"
api_key = os.environ.get("API_KEY")
own_email = os.environ.get("OWN_EMAIL")
own_password = os.environ.get("OWN_PASSWORD")
to_email = os.environ.get("TO_EMAIL")

if not all([api_key, own_email, own_password, to_email]):
    print("❌ Critical System Error: One or more environment secrets are completely missing.")
    print("Check that your variable declarations are uppercase in your YAML workflow profiles.")
    exit(1)

MY_LAT = 6.4549
MY_LONG = 3.4246

weather_params = {
    "lat": MY_LAT,
    "lon": MY_LONG,
    "appid": api_key,
    "cnt": 4,
}

response = requests.get(OWM_Endpoint, params=weather_params, timeout=15)
response.raise_for_status()
weather_data = response.json()

will_rain = False
for hour_data in weather_data["list"]:
    condition_code = hour_data["weather"][0]["id"]
    if int(condition_code) < 700:
        will_rain = True

if will_rain:
    email_message = "Subject: Weather Warning 🌧️☔\n\nIt's going to rain today. Remember to bring an umbrella."
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
            connection.login(own_email, own_password)
            connection.sendmail(own_email, to_email, email_message)
    except (smtplib.SMTPException, TimeoutError):
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(own_email, own_password)
            connection.sendmail(own_email, to_email, email_message)

