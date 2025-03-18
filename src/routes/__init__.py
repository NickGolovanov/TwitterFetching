from flask import Blueprint
from .geo_data import ns as geo_data_ns
from .information import ns as information_ns
from .post import ns as post_ns
from .social_media import ns as social_media_ns
from .user import ns as user_ns
from .pipeline import ns as pipeline_ns

# Create a main blueprint to register all other blueprints
main_routes = Blueprint('main', __name__)

# Register each blueprint with appropriate URL prefix
main_routes.register_blueprint(social_media_ns, url_prefix='/social_media')
main_routes.register_blueprint(geo_data_ns, url_prefix='/geo_data')
main_routes.register_blueprint(information_ns, url_prefix='/information')
main_routes.register_blueprint(post_ns, url_prefix='/post')
main_routes.register_blueprint(user_ns, url_prefix='/user')
main_routes.register_blueprint(pipeline_ns, url_prefix='/pipeline')
