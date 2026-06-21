from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Home Network Monitor</h1><p>Welcome to the home network monitoring dashboard.</p>"







if __name__ == "__main__":
    app.run(debug=True)
