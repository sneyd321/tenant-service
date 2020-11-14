from . import tenant
from flask import request, Response, jsonify
import json, requests

from server.api.models import Tenant



@tenant.route("/Tenant", methods=["POST"])
def create_tenant():
    data = request.get_json()
    try:
        tenant = Tenant(data)
        tenant.generatePasswordHash(data["password"])
        if tenant.insert():
            return jsonify(tenant.toJson())
        return Response(response="Error: Conflict in database", status=409)
    except KeyError:
        return Response(response="Error: Data in invalid format", status=400)


@tenant.route("Tenant/<int:tenantId>/approve", methods=["PUT"])
def update_tenant(tenantId):
    data = request.get_json()
    tenant = Tenant.query.filter(Tenant.id == tenantId).first()
    tenant.isApproved = data["isApproved"]
    if tenant.update(): 
        print(tenant.toJson())  
        return jsonify(tenant.toJson())
    return Response(response="Error: Update failed on concurrent update", status=409)

@tenant.route("/House/<int:houseId>/Tenant")
def get_tenants_by_house_id(houseId):
    data = request.get_json()
    tenants = Tenant.query.filter(Tenant.houseId == houseId).all()
 
    return jsonify([tenant.toJson() for tenant in tenants])
    


@tenant.route("Tenant/<int:tenantId>", methods=["GET"])
def load_tenant(tenantId):
    tenant = Tenant.query.get(tenantId)
    if tenant:
        return jsonify(tenant.toJson())
    return Response(response="Error: Record does not exist", status=404)

@tenant.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    tenant = Tenant.query.filter(Tenant.email == data["email"]).first()
    if tenant and tenant.verifyPassword(data["password"]):
        return jsonify(tenant.toJson())
    return Response(response="Error account not found", status=401)