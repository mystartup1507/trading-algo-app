from flask import Flask, jsonify
from account import account_service

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({
        "success": True,
        "message": "MT5 Bridge Running"
    })

@app.route("/account")
def account():

    result = account_service.get_account_info()

    return jsonify(result)

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )

@app.route("/account")
def account():

    result = account_service.get_account_info()

    return jsonify(result)
