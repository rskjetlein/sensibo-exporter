import os
import time
import requests
from flask import Flask, Response

app = Flask(__name__)

API_KEY   = os.getenv("API_KEY")
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

    url = f"https://api.sensibo.com/v2/devices/{DEVICE_ID}/measurements?limit=1"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        r = requests.get(url, headers=headers, timeout=8)
    except Exception:
        return None

    if r.status_code != 200:
        return None

    try:
        json_data = r.json()
        latest = json_data["data"]["measurements"][0]
        temp = latest.get("temperature")
        humidity = latest.get("humidity")
    except Exception:
        return None

    data = {"temp": temp, "humidity": humidity}

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

    metrics = [
        "# HELP sensibo_temperature_celsius Current temperature in Celsius",
        "# TYPE sensibo_temperature_celsius gauge",
        f"sensibo_temperature_celsius{{device=\"{DEVICE_ID}\"}} {data['temp']}",

        "# HELP sensibo_humidity_relative Relative humidity in percent",
        "# TYPE sensibo_humidity_relative gauge",
        f"sensibo_humidity_relative{{device=\"{DEVICE_ID}\"}} {data['humidity']}",
    ]

    return Response("\n".join(metrics) + "\n", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
