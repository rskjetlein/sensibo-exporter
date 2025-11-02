import os
import time
import requests
from flask import Flask, Response

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
DEVICE_ID = os.getenv("DEVICE_ID")

CACHE_TTL = 10  # seconds
_cache = {"ts": 0, "data": None}


def fetch_measurements():
    now = time.time()

    if not API_KEY or not DEVICE_ID:
        return None

    # Cache hit
    if now - _cache["ts"] < CACHE_TTL and _cache["data"] is not None:
        return _cache["data"]

    url = (
        f"https://home.sensibo.com/v2/devices/{DEVICE_ID}"
        "?apiKey={API_KEY}"
        "&fields=measurements,acState,room"
    )

    try:
        r = requests.get(url, headers=headers, timeout=8)
    except Exception:
        return None

    if r.status_code != 200:
        return None

    try:
        json_data = r.json()
        device_data = json_data["data"]

        measurements = device_data["measurements"][0]
        ac_state = device_data.get("acState", {})
        room_name = device_data.get("room", {}).get("name", "unknown")

        temp = measurements.get("temperature")
        humidity = measurements.get("humidity")
        setpoint = ac_state.get("targetTemperature")

    except Exception:
        return None

    data = {
        "temp": temp,
        "humidity": humidity,
        "setpoint": setpoint,
        "room_name": room_name,
    }

    _cache["ts"] = now
    _cache["data"] = data
    return data


@app.route("/metrics")
def metrics():
    if not API_KEY or not DEVICE_ID:
        return Response("Error: API_KEY or DEVICE_ID not set\n", status=500)

    data = fetch_measurements()
    if data is None:
        return Response("Error retrieving Sensibo metrics\n", status=500)

    labels = f'device="{DEVICE_ID}",room="{data["room_name"]}"'

    metrics = [
        "# HELP sensibo_temperature_celsius Current measured temperature (C)",
        "# TYPE sensibo_temperature_celsius gauge",
        f"sensibo_temperature_celsius{{{labels}}} {data['temp']}",

        "# HELP sensibo_humidity_relative Relative humidity (%)",
        "# TYPE sensibo_humidity_relative gauge",
        f"sensibo_humidity_relative{{{labels}}} {data['humidity']}",

        "# HELP sensibo_temperature_setpoint_celsius Temperature setpoint (C)",
        "# TYPE sensibo_temperature_setpoint_celsius gauge",
        f"sensibo_temperature_setpoint_celsius{{{labels}}} {data['setpoint']}",
    ]

    return Response("\n".join(metrics) + "\n", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
