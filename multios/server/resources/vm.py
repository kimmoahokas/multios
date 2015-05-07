__author__ = 'Kimmo Ahokas'

from flask import url_for
from flask.ext.restful import fields, Resource, reqparse, abort, marshal_with
from multios.base.exceptions import MultiOSError
from multios.server import app, api, scheduler, os_instances


def get_vm_instance_url(vm_instance):
    return url_for('vm', _external=True,
                   os_id=os_instances.index(vm_instance.openstack),
                   vm_id=vm_instance.id)

vm_fields = {
    'name': fields.String,
    'id': fields.String(),
    'url': fields.String(attribute=get_vm_instance_url),
    'os_name': fields.String(attribute=lambda x: x.openstack.name),
    # TODO: how to get IP addresses?
}

@api.resource('/vm')
class VMList(Resource):
    @marshal_with(vm_fields)
    def get(self):
        app.logger.debug('VMList.get() called')
        vm_list = []
        for os in os_instances:
            vm_list.extend(os.vm_instances)
        return vm_list

    @marshal_with(vm_fields)
    def post(self):
        app.logger.debug('VMList.post() called')

        parser = reqparse.RequestParser()
        parser.add_argument('type', type=str, required=True,
                            choices=app.config['TYPES'].keys(),
                            help='Invalid or missing instance type')
        parser.add_argument('count', type=int, default=1,
                            help='Invalid number of instances to be created')
        args = parser.parse_args()

        params = app.config['TYPES'][args['type']]
        params['count'] = args['count']

        os_instance = scheduler.schedule()
        app.logger.info('Launching {} new VM instance with type {} to OS '
                        'instance {}'.format(
            args['count'], args['type'], os_instance.name))
        vm_instance = None
        try:
            vm_instance = os_instance.launch_instance(params)
        except MultiOSError as e:
            app.logger.error('MultiOSError at VMList.post()', exc_info=e)
            abort(500, message=e.message)
        return vm_instance

    def delete(self):
        vm_instance = scheduler.schedule_deletion()
        vm_instance.delete()
        return {'status': 'Successfully deleted instance {}'.format(
            vm_instance.id)}


@api.resource('/vm/<string:vm_id>')
class VM(Resource):
    @marshal_with(vm_fields)
    def get(self, vm_id):
        app.logger.debug('VM.get() called with id %s', vm_id)
        return self._find_instance(vm_id)

    def delete(self, vm_id):
        app.logger.debug('VM.delete() called with id %s', vm_id)
        vm = self._find_instance(vm_id)
        vm.delete()
        return {'status': 'Successfully deleted instance {}'.format(vm_id)}

    def _find_instance(self, vm_id):
        for os in os_instances:
            try:
                vm = os.find_vm_instance(vm_id)
                if vm is not None:
                    return vm
            except MultiOSError:
                app.logger.debug("Instance not found from OS {}".format(
                    os.name))
        abort(404, info='Instance not found')

