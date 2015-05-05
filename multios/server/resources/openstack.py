__author__ = 'Kimmo Ahokas'

from flask import url_for
from flask.ext.restful import Resource, fields, marshal_with, abort

from multios.server import app, os_instances


def get_os_instance_url(os_instance):
    return url_for('openstack', _external=True,
                   os_id=os_instances.index(os_instance))


os_fields = {
    'name': fields.String,
    'id': fields.Integer(attribute=lambda x: os_instances.index(x)),
    'url': fields.String(attribute=get_os_instance_url),
    'auth_url': fields.String(),
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


class OpenStackList(Resource):
    @marshal_with(os_fields)
    def get(self):
        return os_instances


class OpenStack(Resource):
    @marshal_with(os_fields)
    def get(self, os_id):
        # TODO: error handling
        os = None
        try:
            os = os_instances[os_id]
        except IndexError:
            abort(404, reason='Invalid instance id: {}'.format(os_id))
        return os
