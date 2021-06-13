from . import tenant
from flask import request, Response, jsonify, render_template
import json, requests
from server.api.forms import TenantForm
from server.api.models import Tenant
from server.api.RequestManager import Zookeeper, RequestManager


zookeeper = Zookeeper()



def get_homeowner_gateway():
    return "192.168.0.108:8079"




@tenant.route("/")
def get_sign_up_form():
    global zookeeper
    service = zookeeper.get_service("tenant-gateway")
    service = get_homeowner_gateway()
    if service:
        form = TenantForm()
        return render_template("signupTemplate.html", form=form, fields=list(form._fields.values()), conflict="", url="http://" + service + "/tenant-gateway/v1/")
    return Response(response="Error: Zookeeper down", status=503)

    

@tenant.route("/", methods=["POST"])
def sign_up():
    global zookeeper
    service = zookeeper.get_service("tenant-gateway")
    service = get_homeowner_gateway()
    if service:
        form = TenantForm(request.form)
        attrs = list(form._fields.values())
        if form.validate():
            tenant = Tenant(**request.form)
            tenant.generatePasswordHash(request.form.get("password"))
            if tenant.insert():
                return Response(response="FormComplete", status=201)
            return render_template("signupTemplate.html", form=form, fields=attrs, conflict="Error: Account already exists", url="http://" + service + "/tenant-gateway/v1/")
        return render_template("signupTemplate.html", form=form, fields=attrs, conflict="", url="http://" + service + "/tenant-gateway/v1/")
    return Response(response="Error: Zookeeper down", status=503)
   



@tenant.route("Tenant/<int:tenantId>/Approve", methods=["PUT"])
def update_tenant(tenantId):
    data = request.get_json()
    tenant = Tenant.query.filter(Tenant.id == tenantId).first()
    if tenant:
        tenant.isApproved = data["isApproved"]        
        if tenant.update():             
            tenants = Tenant.query.filter(Tenant.houseId == tenant.houseId).all()
            return jsonify([tenant.toJson() for tenant in tenants])
        return Response(response="Error: Update failed on concurrent update", status=409)
    return Response(response="Error: Tenant does not exist", status=404)


@tenant.route("House/<int:houseId>/Tenant")
def get_tenants_by_house_id(houseId):
    tenants = Tenant.query.filter(Tenant.houseId == houseId).all()
    if tenants:
        return jsonify([tenant.toJson() for tenant in tenants])
    return jsonify([])


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
    #If email exists
    if tenant:
        #If password exists
        if tenant.verifyPassword(request.authorization.password):
            #Get login data from json request
            loginData = request.get_json()
            #If tenant house id matches house id in login
            if tenant.houseId == loginData["houseId"]:
                #If tenant is approved
                if tenant.isApproved:
                    
                    #return tenant
                    return jsonify(tenant.toJson())  
                return Response(response="Tenant not approved", status=403)
            #If house id does not match
            else:
                tenant.houseId = loginData["houseId"]
                tenant.isApproved = False
                if tenant.update():
                    return Response(response="House Id Updated to " + str(tenant.houseId), status=400)
                return Response(response="Failed to update house id", status=400)
            return Response(response="Error invalid house Id", status=404)
        return Response(response="Error invalid account credentials", status=401)
    return Response(response="Error account not found", status=404)


    
