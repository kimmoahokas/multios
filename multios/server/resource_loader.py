__author__ = 'Kimmo Ahokas'

from multios.server.resources.openstack import OpenStackList, OpenStack
from multios.server.resources.vm import VMList, VM


def load_resources(app, api):
    """Load Flask-Restful API resources.
    :param app: Flask APP instance
    :param api: Flask-Restful API instance
    :return: None
    """

    app.logger.debug('Loading API resources...')

    #
    api.add_resource(OpenStackList, '/os')
    api.add_resource(OpenStack, '/os/<string:os_id>')

    api.add_resource(VMList, '/vm')
    api.add_resource(VM, '/vm/<string:vm_id>')

    app.logger.debug('API resources successfully loaded')