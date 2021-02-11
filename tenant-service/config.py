import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

    def __init__(self, app):
        self.app = app

    def productionConfig(self):    
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://admin:admin@mysql:3306/roomr"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["SECRET_KEY"] = "FDSAFASFDASFDASGBFRSHBDSSFASDF"
        return self.app

    def developmentConfig(self):    
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@host.docker.internal:3306/roomr"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["SECRET_KEY"] = "FDSAFASFDASFDASGBFRSHBDSSFASDF"
        return self.app

    def testConfig(self):
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, 'test.db')
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        return self.app
