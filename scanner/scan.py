import requests, re, socket, subprocess, uuid


def get_vendor(mac):

    if not mac or mac == "-":
        return "Unknown"

    try:

        response = requests.get(
            f"https://api.macvendors.com/{mac}",
            timeout=3
        )

        if response.status_code == 200:
            return response.text

    except Exception:
        pass

    return "Unknown"


def run_map(network):

    my_ip = socket.gethostbyname(socket.gethostname())

    my_mac = ':'.join(
        f'{(uuid.getnode() >> i) & 0xff:02X}'
        for i in range(40, -1, -8)
    )

    result = subprocess.run(
        ["nmap", "-sn", network],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        return [{
            "host": "Scan Error",
            "ip": "-",
            "mac": "-",
            "vendor": "-",
            "latency": "-"
        }]

    devices = {}

    current = None

    for line in result.stdout.splitlines():

        if "Nmap scan report for" in line:

            if current and "ip" in current:
                devices[current["ip"]] = current

            current = {
                "host": "Unknown",
                "ip": "",
                "mac": "-",
                "vendor": "-",
                "latency": "N/A"
            }

            match = re.search(
                r"Nmap scan report for (.+?)(?: \((.*?)\))?$",
                line
            )

            if match:

                if match.group(2):
                    current["host"] = match.group(1)
                    current["ip"] = match.group(2)
                else:
                    current["ip"] = match.group(1)

        elif "MAC Address:" in line and current:

            mac = re.search(
                r"MAC Address: ([A-Fa-f0-9:]+)",
                line
            )

            if mac:

                current["mac"] = mac.group(1)

                if current["ip"] == my_ip:
                    current["mac"] = my_mac

                current["vendor"] = get_vendor(
                    current["mac"]
                )

        elif "latency" in line and current:

            latency = re.search(
                r"\(([^)]+)\s+latency\)",
                line
            )

            if latency:
                current["latency"] = latency.group(1)

    if current and "ip" in current:
        devices[current["ip"]] = current

    return list(devices.values())



if __name__ == "__main__":
    print("Scanner started....")

    network = "192.168.1.0/24"

    print("Running nmap....")

    devices = run_map(network)

    # post to flask server
    requests.post(
        "http://127.0.0.1:8000/api/upload",
        json=devices
    )



