from flask import Flask, Response
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()
app = Flask(__name__)

from kazoo.client import KazooClient, KazooState

zk = KazooClient(hosts='host.docker.internal:2181')
zk.start()



@app.route("/Health")
def health_check():
    return Response(status=200)


def create_app(env):
    #Create app
    global app
    config = Config(app)

    if env == "prod":
        app = config.productionConfig()
    elif env == "dev":
        app = config.developmentConfig()
    elif env == "test":
        app = config.testConfig()
    else:
        return 
    
    migrate = Migrate(app, db)
    db.init_app(app)
    
    #Intialize modules
    from server.api.routes import tenant
    app.register_blueprint(tenant, url_prefix="/tenant/v1")
    return app