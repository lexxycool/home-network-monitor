
from flask import Flask, render_template, jsonify
import subprocess, re

app = Flask(__name__)

def run_map():
    result = subprocess.run(
        ["nmap", "-sn", "192.168.1.0/24"], 
        capture_output=True, 
        text=True
    )

    devices = []

    current = {}

    for line in result.stdout.splitlines():
        if "Nmap scan report for" in line:
            if current:
                devices.append(current)
            current = {}

            match = re.search(r"Nmap scan report for (.*?) \((.*?)\)", line)
            if match:
                current["host"] = match.group(1)
                current["ip"] = match.group(2)
            elif "MAC Address" in line:
                mac = re.search(r"MAC Address: ([A-Fa-f0-9:]+)", line)
                if mac:
                    current["mac"] = mac.group(1)
            elif "Host is up" in line:
                latency = re.search(r"\((.*? ) latency\)", line)
                if latency:
                    current["latency"] = latency.group(1)
        
        if current:
            devices.append(current)

    return devices


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan")
def scan():
    devices = run_map()
    return jsonify(devices)



if __name__ == "__main__":
    app.run(debug=True)
