import random

__author__ = 'Kimmo Ahokas'


class Scheduler(object):
    def __init__(self, os_instances):
        self._os_instances = os_instances

    def schedule(self):
        """
        Select OpenStack instance for creating next VM

        New instance will be created to OpenStack with smallest number of
        running virtual machines to ensure maximum resilience.

        :return: OpenStackInstance to be used for the VM
        :rtype: multios.base.os_instance.OpenStackInstance
        """
        instance = min(self.get_managed_instance_counts())[1]
        return instance

    def schedule_deletion(self):
        """
        Select virtual machine instance to be deleted

        Delete the virtual machine from OpenStack with highest number of
        virtual machines. Then randomly select one of the virtual machines
        for deletion.

        :return: VMInstance that should be deleted
        :rtype: multios.base.vm_instance.VMInstance
        """
        os_instance = max(self.get_managed_instance_counts())[1]
        vm_instances = os_instance.vm_instances
        return random.choice(vm_instances)

    def get_managed_instance_counts(self):
        """
        :return: number of MultiOS-managed vm instances in each of the
        OpenStacks.
        :rtype: list(tuple(int, multios.base.os_instance.OpenStackInstance))
        """
        counts = [(x.vm_count, x) for x in self._os_instances]
        return counts