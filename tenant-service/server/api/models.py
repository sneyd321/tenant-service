from werkzeug.security import generate_password_hash, check_password_hash
from server import db, app
from sqlalchemy.exc import IntegrityError, OperationalError
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(120), index=True, unique=True)
    phoneNumber = db.Column(db.String(15))
    password = db.Column(db.String(100))
    isApproved = db.Column(db.Boolean())
    imageURL = db.Column(db.String(250), nullable=True)
    houseId = db.Column(db.Integer(), nullable=False)

    def __init__(self, **tenantData):
        self.firstName = tenantData.get("firstName", "")
        self.lastName = tenantData.get("lastName", "")
        self.email = tenantData.get("email", "")
        self.password = tenantData.get("password", "")
        self.phoneNumber = tenantData.get("phoneNumber", "")
        self.isApproved = False
        self.houseId = 0
        self.imageURL = None

    def generatePasswordHash(self, password):
        self.password = generate_password_hash(password)
        
    def verifyPassword(self, password):
        return check_password_hash(self.password, password)

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError:
            db.session.rollback()
            return False


    
    def update(self):
        rows = Tenant.query.filter(Tenant.email == self.email).update(self.toDict(), synchronize_session=False)
        if rows == 1:
            try:
                db.session.commit()
                return True
            except OperationalError:
                db.session.rollback()
                return False
        return False
            

    def toDict(self):
        return {
            Tenant.firstName: self.firstName,
            Tenant.lastName: self.lastName,
            Tenant.email: self.email,
            Tenant.password: self.password,
            Tenant.isApproved: self.isApproved,
            Tenant.phoneNumber: self.phoneNumber,
            Tenant.imageURL: self.imageURL
        }

    def getId(self):
        return {
            "tenantId": self.id
        }

    def toJson(self):
        return {
            "tenantId": self.id,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "isApproved": self.isApproved,
            "houseId": self.houseId,
            "phoneNumber": self.phoneNumber,
            "imageURL": self.imageURL
        }

    def getAuthToken(self):
        return {
            "authToken": self.generate_auth_token().decode("utf-8"),
        }
    

    def generate_auth_token(self, expiration = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            return Tenant.query.get(data['id'])
        except SignatureExpired:
            return None 
        except BadSignature:
            return None # invalid token

    def __repr__(self):
        return "< Tenant: " + self.firstName + " " + self.lastName + " >"