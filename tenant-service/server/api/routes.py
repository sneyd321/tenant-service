from . import tenant
from flask import request, Response, jsonify, render_template
import json, requests
from server.api.forms import TenantForm
from server.api.models import Tenant
from server.api.RequestManager import Zookeeper, RequestManager
from server import app

zookeeper = Zookeeper()


def get_homeowner_gateway():
    return "34.107.132.144"

@tenant.route("/")
def get_sign_up_form():
    service = get_homeowner_gateway()

    form = TenantForm()
    return render_template("signupTemplate.html", form=form, fields=list(form._fields.values()), conflict="", url="http://" + service + "/tenant-gateway/v1/")


    

@tenant.route("/", methods=["POST"])
def sign_up():
    service = get_homeowner_gateway()

    form = TenantForm(request.form)
    attrs = list(form._fields.values())
    if form.validate():
        tenant = Tenant(**request.form)
        tenant.generatePasswordHash(request.form.get("password"))
        if tenant.insert():
            return Response(response="FormComplete", status=201)
        return render_template("signupTemplate.html", form=form, fields=attrs, conflict="Error: Account already exists", url="http://" + service + "/tenant-gateway/v1/")
    return render_template("signupTemplate.html", form=form, fields=attrs, conflict="", url="http://" + service + "/tenant-gateway/v1/")




@tenant.route("Tenant/<int:tenantId>/Approve", methods=["PUT"])
def update_tenant(tenantId):
    tenantData = request.get_json()
    if not tenantData or "isApproved" not in tenantData:
        return Response(response="Error: Invalid request", status=400)
    tenant = Tenant.query.get(tenantId)
    tenant.isApproved = tenantData["isApproved"]        
    if tenant.update():             
        tenants = Tenant.query.filter(Tenant.houseId == tenant.houseId).all()
        return jsonify([tenant.toJson() for tenant in tenants])
    return Response(response="Error: Update failed on concurrent update", status=409)



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
        return Response(response="Error: Tenant Not Found", status=404)
    return Response(response="Not Authenticated", status=401)




@tenant.route("Tenant/<int:tenantId>", methods=["GET"])
def get_tenant_by_id(tenantId):
    
        tenant = Tenant.query.get(tenantId)
        if tenant:
            return jsonify(tenant.toJson())
        return Response(response="Error: Tenant Not Found", status=404)
   

@tenant.route("/Verify", methods=["GET"])
def verify_tenant():
    bearer = request.headers.get("Authorization")
    if bearer:
        tenant = Tenant.verify_auth_token(bearer[7:])
        if tenant:
            return jsonify(tenant.getId())
        return Response(response="Not Found", status=404)
    return Response(response="Not Authenticated", status=401)



@tenant.route("/Login", methods=["POST"])
def login():
    if request.authorization == None:
        return Response(response="Missing Authrozation", status=400)

    loginData = request.get_json()
    if not loginData or not "houseId" in loginData:
        return Response(response="Please enter a house Id", status=400)

    try:
        houseId = int(loginData["houseId"])
    except ValueError:
        return Response(response="Invalid House Id", status=400)
    except TypeError:
        return Response(response="Invalid House Id", status=400)

    tenant = Tenant.query.filter(Tenant.email == request.authorization.username).first()
    if tenant:
        if tenant.verifyPassword(request.authorization.password):
            if tenant.houseId == loginData["houseId"]:
                if tenant.isApproved:
                    return jsonify(tenant.getAuthToken())  
                return Response(response="Not Approved", status=403)
            else:
                tenant.houseId = loginData["houseId"]
                tenant.isApproved = False
                if tenant.update():
                    return Response(response="House Id Updated to " + str(tenant.houseId), status=400)
                return Response(response="Failed to update house id", status=400)
            return Response(response="Error invalid house Id", status=404)

        return Response(response="Error invalid account credentials", status=401)
    return Response(response="Error invalid account credentials", status=401)


    
@tenant.route("Tenant/<int:tenantId>/imageURL", methods=["PUT"])
def update_imageURL(tenantId):
    tenantData = request.get_json()
    if not tenantData or "imageURL" not in tenantData:
        return Response(response="Error: Invalid Request Body", status=400)
   
    tenant = Tenant.query.get(tenantId)
    tenant.imageURL = tenantData["imageURL"]
    if tenant.update():
        return jsonify(tenant.toJson())
    return Response(response="Error: Failed to update tenant", status=409)