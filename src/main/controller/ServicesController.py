from flask import Blueprint, jsonify
from src.main.db.models import Service

services_bp = Blueprint("services_bp", __name__, url_prefix="/api/services")

@services_bp.route("/list", methods=["GET"])
def list_services():
    services = Service.query.all()
    return jsonify([service.to_dict() for service in services]), 200