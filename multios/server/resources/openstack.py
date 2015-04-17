__author__ = 'Kimmo Ahokas'


from flask.ext.restful import Resource, fields, marshal_with, abort

from multios.server import app, api, os_instances

os_fields = {
    'name': fields.String,
    'auth_url': fields.String,
    'tenant': fields.String(attribute='tenant_name'),
    'region': fields.String(attribute='region_name'),
    'keystone': fields.String(attribute=lambda os: os.get_keystone_info()),
    'glance': fields.String(attribute=lambda os: os.get_glance_info()),
    'nova': fields.String(attribute=lambda os: os.get_nova_info()),
    'neutron': fields.String(attribute=lambda os: os.get_neutron_info()),
    'cinder': fields.String(attribute=lambda os: os.get_cinder_info()),
    'ceilometer': fields.String(attribute=lambda os: os.get_ceilometer_info()),
    'heat': fields.String(attribute=lambda os: os.get_heat_info()),
}


@api.resource('/os')
class OpenStackList(Resource):
    @marshal_with(os_fields)
    def get(self):
        app.logger.debug('OpenStackList.get() called')
        return os_instances


@api.resource('/os/<int:os_id>')
class OpenStack(Resource):
    @marshal_with(os_fields)
    def get(self, os_id):
        app.logger.debug('OpenStack.get() called with id {}'.format(os_id))
        # TODO: error handling
        os = None
        try:
            os = os_instances[os_id]
        except IndexError:
            abort(404, reason='Invalid instance id: {}'.format(os_id))
        return os
