class ConsulBackendException(Exception):
    pass


class NoServerFound(ConsulBackendException):
    '''
    Raised when no consul server can be contacted.
    '''
