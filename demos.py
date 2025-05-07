from flask import Flask
import modules, common_routes

app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'CHANGEME',
    'SESSION_COOKIE_HTTPONLY': False,
	
})

app.register_blueprint(common_routes.app)
app.register_blueprint(modules.brokenaccess.app)
app.register_blueprint(modules.brokenauth1.app)
app.register_blueprint(modules.brokenauth2.app)
app.register_blueprint(modules.brokensession.app)
app.register_blueprint(modules.inject.app)
app.register_blueprint(modules.secmis.app)
app.register_blueprint(modules.xss.app)
app.register_blueprint(modules.paramtamp.app)
app.register_blueprint(modules.pathtraversal.app)
		
if __name__ == "__main__":
		app.run()