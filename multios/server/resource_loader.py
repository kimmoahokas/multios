__author__ = 'Kimmo Ahokas'


from multios.server.resources.vm import VM


def load_resources(app, api):
    """Load Flask-Restful API resources.
    :param app: Flask APP instance
    :param api: Flask-Restful API instance
    :return: None
    """

    app.logger.debug('Loading API resources...')

    api.add_resource(VM, '/vm', '/vm/<string:id>')

    app.logger.debug('API resources successfully loaded')