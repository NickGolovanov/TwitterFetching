from flask import Blueprint
from .geo_data import geo_data_route
from .information import information_route
from .post import post_route
from .social_media import social_media_routes
from .user import user_routes
from .pipeline import pipeline_route

main_routes = Blueprint('main', __name__)

main_routes.register_blueprint(social_media_routes, url_prefix='/social_media')
main_routes.register_blueprint(geo_data_route, url_prefix='/geo_data')
main_routes.register_blueprint(information_route, url_prefix='/information')
main_routes.register_blueprint(post_route, url_prefix='/post')
main_routes.register_blueprint(user_routes, url_prefix='/user')
main_routes.register_blueprint(pipeline_route, url_prefix='/pipeline')