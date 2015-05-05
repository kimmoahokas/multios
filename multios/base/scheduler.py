__author__ = 'Kimmo Ahokas'


class Scheduler(object):
    def __init__(self, os_instances):
        self._os_instances = os_instances
        self.next_instance = 0

    def schedule(self):
        """
        Select OpenStack instance for creating next VM
        :return: OpenStackInstance to be used for the VM
        :rtype: multios.base.os_instance.OpenStackInstance
        """

        # TODO: ensure that all os instance have same amount of virtual
        # machines running
        current = self.next_instance
        self.next_instance = (self.next_instance + 1) % len(self._os_instances)
        return self._os_instances[current]