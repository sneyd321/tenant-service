from . import tenant
from flask import request, Response, jsonify
import json, requests

from server.api.models import Tenant



@tenant.route("/Tenant", methods=["POST"])
def create_tenant():
    data = request.get_json()
    try:
        user = Tenant(data)
        if user.insert():
            return Response(status=201)
        return Response(response="Error: Conflict in database", status=409)
    except KeyError:
        return Response(response="Error: Data in invalid format", status=400)


@tenant.route("/Tenant/<int:id>", methods=["PUT"])
def update_tenant(id):
    data = request.get_json()
    user = Tenant(data)
    if user.update():
        return Response(status=200)
    return Response(response="Error: Update failed on concurrent update", status=409)


@tenant.route("Tenant/<int:id>", methods=["GET"])
def load_tenant(id):
    user = Tenant.query.get(id)
    if user:
        return jsonify(user.toJson())
    return Response(response="Error: Record does not exist", status=404)