# from flask import Flask
# app = Flask(__name__)
# @app.route('/')
# def hello():
#     return '<h1>Hello, World!</h1>'
# if __name__ == '__main__':
#     app.run(debug=True)

# from flask import Flask
# # from werkzeug.middleware.proxy_fix import ProxyFix

# # from ragbackend.main import settings

# from flask_talisman import talisman
# def init_app(app):
#     talisman.init_app(
#         app
#     )


from flask import Flask
from flask_cors import CORS, cross_origin

class Rags(Flask):
    """A custom Flask app for Rag"""

    def __init__(self, *args, **kwargs):
        super(Rags, self).__init__(__name__, *args, **kwargs)
        self.config["FLASK_ENV"] = "development"
        self.config["FLASK_DEBUG"] = True
        self.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.config["PROPAGATE_EXCEPTIONS"] = True
  

def create_app():
    from . import (
        main
    )  

    app = Rags()
    
    main.init_app(app)

    return app
