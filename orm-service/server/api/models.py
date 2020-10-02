from werkzeug.security import generate_password_hash, check_password_hash
from server import db
from sqlalchemy.exc import IntegrityError, OperationalError


class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(100))
    isApproved = db.Column(db.Boolean())
    houseId = db.Column(db.Integer(), nullable=False)

    def __init__(self, tenantData):
        self.firstName = tenantData["firstName"]
        self.lastName = tenantData["lastName"]
        self.email = tenantData["email"]
        self.password = generate_password_hash(tenantData["password"])
        self.isApproved = tenantData["isApproved"]
        self.houseId = tenantData["houseId"]
        
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
            Tenant.isApproved: self.isApproved
        }

    def toJson(self):
        return {
            "tenantId": self.id,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "password": self.password,
            "isApproved": self.isApproved,
            "houseId": self.houseId
        }

    def __repr__(self):
        return "< Tenant: " + self.firstName + " " + self.lastName + " >"