from flask import Flask
import os
app = Flask(__name__)

COLOR = os.getenv("COLOR", "blue")
VERSION = os.getenv("VERSION", "dev")

@app.route("/")
def hello():
    return f"Hello from Flask! Active color: {COLOR}, version: {VERSION}\n"

@app.route("/healthz")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

