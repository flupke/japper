class Backend(object):
    '''
    Generic base-class for pluggable backends.
    '''

    app_name = None

    def _guess_package(self):
        return self.__class__.__module__.rpartition('.')[0]

    def get_app_name(self):
        '''
        Return the registered app name for this backend, i.e. what goes into
        INSTALLED_APPS.

        The default is the name of the package in which the backend is defined.
        Define :attr:`app_name` to override.
        '''
        if self.app_name is not None:
            return self.app_name
        return self._guess_package()

