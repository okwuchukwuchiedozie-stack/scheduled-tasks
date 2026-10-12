import requests
import smtplib
import os

OWM_Endpoint = "https://api.openweathermap.org/data/2.5/forecast"
api_key = os.environ.get("API_KEY")
own_email = os.environ.get("OWN_EMAIL")
own_password = os.environ.get("OWN_PASSWORD")
to_email = os.environ.get("TO_EMAIL")

MY_LAT = 6.4549
MY_LONG = 3.4246

weather_params = {
        "lat": MY_LAT,
        "lon": MY_LONG,
        "appid": api_key,
        "cnt": 4,
    }

response = requests.get(OWM_Endpoint, params=weather_params)
response.raise_for_status()
weather_data = response.json()

will_rain = False
for hour_data in weather_data["list"]:
    condition_code = hour_data["weather"][0]["id"]
    if int(condition_code) < 700:
        will_rain = True
if will_rain:
    email_message = "It's going to rain today. Remember to bring an umbrella. 🌧️☔"
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
            connection.login(own_email, own_password)
            connection.sendmail(own_email, to_email, email_message)
    except TimeoutError:
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(own_email, own_password)
            connection.sendmail(own_email, to_email, email_message)
