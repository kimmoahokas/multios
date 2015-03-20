__author__ = 'Kimmo Ahokas'

from flask.ext.restful import Resource

from multios.server import app


class VMList(Resource):
    def get(self):
        app.logger.debug('VMList.get() called')
        return 'Should list virtual machines'

    def post(self):
        app.logger.debug('VMList.post() called')
        return 'Should create new VM instance now...'


class VM(Resource):
    def get(self, vm_id):
        app.logger.debug('VM.get() called with id %s', vm_id)
        return 'Should print information about given vm'

    def post(self):
        pass

