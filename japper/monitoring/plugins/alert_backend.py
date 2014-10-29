import abc

import six

from .backend import Backend


class AlertBackend(six.with_metaclass(abc.ABCMeta, Backend)):
    '''
    Base class for alert backends.
    '''

    @abc.abstractmethod
    def send_alert(self, user, prev_state, new_state):
        '''
        Send an alert to *user* when a :class:`japper.monitoring.models.State`
        has changed from *prev_state* to *new_state*.
        '''
