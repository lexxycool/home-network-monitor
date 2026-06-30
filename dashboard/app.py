from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

# stores latest scan from scanner
latest_devices = []


# gets data from local server and upload
@app.route("/api/upload", methods=["POST"])
def upload():
    global latest_devices

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400
    
    latest_devices = data

    return jsonify({
        "message": "Scan uploaded successfully",
        "count": len(latest_devices)
    })


# frontend page
@app.route("/")
def home():
    return render_template("index.html")


# frontend data here
@app.route("/api/devices", methods=["GET"])
def devices():
    print(latest_devices)
    return jsonify(latest_devices)


@app.route("/api/health")
def health():
    return jsonify({
        "status": "running",
        "devices_stored": len(latest_devices)
    })




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)