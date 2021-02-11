from . import tenant
from flask import request, Response, jsonify, render_template
import json, requests
from server.api.forms.TenantForm import TenantForm
from server.api.models import Tenant



@tenant.route("/", methods=["GET", "POST"])
def create_tenant():
    form = TenantForm()
    attrs = list(form._fields.values())
    if request.method == 'POST':
        data = request.form
        print(data)
        tenant = Tenant(data)
        tenant.generatePasswordHash(data["password"])
        if tenant.insert():
            return "<h1>Account successfully created</h1>"
        return render_template("signupTemplate.html", form=form, fields=attrs[:-1], conflict="Error: Account already exists")
    return render_template("signupTemplate.html", form=form, fields=attrs[:-1], conflict="")



@tenant.route("Tenant/<int:tenantId>/approve", methods=["PUT"])
def update_tenant(tenantId):
    data = request.get_json()
    tenant = Tenant.query.filter(Tenant.id == tenantId).first()
    if tenant:
        tenant.isApproved = data["isApproved"]        
        if tenant.update(): 
            print(tenant.toJson())
            tenants = Tenant.query.filter(Tenant.houseId == tenant.houseId).all()            
            return jsonify([tenant.toJson() for tenant in tenants])
        return Response(response="Error: Update failed on concurrent update", status=409)
    return Response(response="Error: Tenant does not exist", status=404)

@tenant.route("House/<int:houseId>/Tenant")
def get_tenants_by_house_id(houseId):
    tenants = Tenant.query.filter(Tenant.houseId == houseId).all()
    return jsonify([tenant.toJson() for tenant in tenants])


@tenant.route("Tenant", methods=["GET"])
def get_tenant():
    bearer = request.headers.get("Authorization")
    if bearer:
        tenant = Tenant.verify_auth_token(bearer[7:])
        if tenant:
            return jsonify(tenant.toJson())
        return Response(response="Error: Record does not exist", status=404)
    return Response(response="Not Authenticated", status=401)


@tenant.route("/Login", methods=["POST"])
def login():
    tenant = Tenant.query.filter(Tenant.email == request.authorization.username).first()
    if tenant:
        if tenant.verifyPassword(request.authorization.password):
            return jsonify(tenant.toJson())
        return Response(response="Error account not found", status=401)
    return Response(response="Error account not found", status=404)


    
