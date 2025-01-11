from flask import Blueprint, jsonify

server_route = Blueprint("server_route", __name__)

@server_route.route("/api", methods=["GET"])
def detect_plaque():
    return jsonify({
        "message": "Your are now connected into Heart Plaque Detection API",
    })