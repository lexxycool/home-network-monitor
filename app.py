
from flask import Flask, render_template, jsonify
import subprocess, re, socket, uuid


app = Flask(__name__, static_folder="static")

def run_map():

    # Get the local IP address
    
    my_ip = socket.gethostbyname(socket.gethostname())

    my_mac = ':'.join(
    f'{(uuid.getnode() >> i) & 0xff:02X}'
    for i in range(40, -1, -8)
)

    result = subprocess.run(
        ["nmap", "-sn", "192.168.1.0/24"], 
        capture_output=True, 
        text=True
    )

    devices = {}

    current = None

    for line in result.stdout.splitlines():
        if "Nmap scan report for" in line:
            if current and "ip" in current:
                devices[current["ip"]] = current
            current = {}

            match = re.search(r"Nmap scan report for (.*?) \((.*?)\)", line)
            if match:
                current["host"] = match.group(1)
                current["ip"] = match.group(2)
                
        elif "MAC Address" in line and current:
                current["mac"] = None
                mac = re.search(r"MAC Address: ([A-Fa-f0-9:]+)", line)
                if mac:
                    current["mac"] = mac.group(1)
                if current["ip"] == my_ip:
                    current["mac"] = my_mac
        elif "Host" in line and current:
                current["latency"] = None
                latency = re.search(r"\((.*? ) latency\)", line)
                if latency:
                    current["latency"] = latency.group(1)
        
    if current and "ip" in current:
        devices[current["ip"]] = current

    return list(devices.values())


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scan")
def scan():
    devices = run_map()
    return jsonify(devices)



if __name__ == "__main__":
    app.run(debug=True)
