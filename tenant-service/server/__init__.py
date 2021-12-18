from flask import Flask, Response
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pymysql
pymysql.install_as_MySQLdb()

db = SQLAlchemy()
app = Flask(__name__)

from kazoo.client import KazooClient, KazooState

zk = KazooClient()




@app.route("/Health")
def health_check():
    return Response(status=200)


def create_app(env):
    #Create app
    global app
    config = Config(app)

    if env == "prod":
        app = config.productionConfig()
        zk.set_hosts('zookeeper.default.svc.cluster.local:2181')
    elif env == "dev":
        app = config.developmentConfig()
        zk.set_hosts('host.docker.internal:2181')
    elif env == "test":
        app = config.testConfig()
    else:
        return 
    
    zk.start()
    migrate = Migrate(app, db)
    db.init_app(app)
    
    #Intialize modules
    from server.api.routes import tenant
    app.register_blueprint(tenant, url_prefix="/tenant/v1")
    return app