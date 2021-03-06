# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys
from importlib import import_module

from flask import Flask, render_template

from app import commands
from app.blueprints import application_blueprints
from app.extension import (
    bcrypt,
    cache,
    csrf_protect,
    debug_toolbar,
    flask_static_digest,
    mail,
)

__all__ = ["create_app"]


def create_app(config_object="app.config"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    register_commands(app)
    configure_logger(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    cache.init_app(app)
    csrf_protect.init_app(app)
    debug_toolbar.init_app(app)
    flask_static_digest.init_app(app)
    mail.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    for ns in application_blueprints:
        import_module(ns.import_name)
        app.register_blueprint(ns)
    return None


def register_error_handlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)


def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
