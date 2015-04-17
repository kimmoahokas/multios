__author__ = 'Kimmo Ahokas'

from flask.ext.restful import Resource, reqparse, abort
from multios.base.exceptions import MultiOSError
from multios.server import app, scheduler


class VMList(Resource):
    def get(self):
        app.logger.debug('VMList.get() called')
        return 'Should list virtual machines'

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
        # TODO: instance names
        params['name'] = args['type']
        params['count'] = args['count']

        os_instance = scheduler.schedule()
        app.logger.info('Launching {} new VM instance with type {} to OS '
                        'instance {}'.format(
            args['count'], args['type'], os_instance.name))
        try:
            instance = os_instance.launch_instance(params)
        except MultiOSError as e:
            abort(e.message)
        return instance


class VM(Resource):
    def get(self, vm_id):
        app.logger.debug('VM.get() called with id %s', vm_id)
        return 'Should print information about given vm'

    def delete(self, vm_id):
        app.loggers.debug('VM.delete() called with id %s', vm_id)

