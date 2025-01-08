from flask import Blueprint, jsonify
from src.main.db.models import Service

# Tworzenie blueprintu dla modułu serwisy
services_bp = Blueprint("services_bp", __name__, url_prefix="/api/services")

# Endpoint wykazu usuług
@services_bp.route("/list", methods=["GET"])
def list_services():
    services = Service.query.all() # Pobranie wsyztskich usuług z bazy danych
    return jsonify([service.to_dict() for service in services]), 200 # Zwrócenie listy usług w formacie JSON