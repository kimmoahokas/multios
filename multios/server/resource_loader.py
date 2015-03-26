__author__ = 'Kimmo Ahokas'

from .resources.openstack import OpenStackList, OpenStack
from .resources.vm import VMList, VM


def load_resources(app, api):
    """Load Flask-Restful API resources.
    :param app: Flask APP instance
    :param api: Flask-Restful API instance
    :return: None
    """

    app.logger.debug('Loading API resources...')

    # Overal OpenStak resources
    api.add_resource(OpenStackList, '/os')
    api.add_resource(OpenStack, '/os/<int:os_id>')

    # Virtual machines
    api.add_resource(VMList, '/vm')
    api.add_resource(VM, '/vm/<string:vm_id>')

    # Virtual networks

    app.logger.debug('API resources successfully loaded')