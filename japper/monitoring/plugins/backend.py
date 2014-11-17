from django.db.models.loading import get_model
import six

from ..exceptions import ImproperlyConfigured


class Backend(object):
    '''
    Generic base-class for pluggable backends.
    '''

    name = None
    app_name = None
    urls_module = None
    create_instance_view = None
    model = None

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

    def get_name(self):
        '''
        Return a descriptive name for the monitoring backend.
        '''
        if self.name is None:
            raise ImproperlyConfigured('subclasses of %s '
                    'must define the name property or reimplement get_name()' %
                    self.__class__.__name__)
        return self.name

    def get_urls_module(self):
        '''
        Return the dotted path to the urls module of the app.

        The default is the name of the package in which the backend class is
        defined appended with ``'.urls'``.  Define :attr:`urls_module` to
        override
        '''
        if self.urls_module is not None:
            return self.urls_module
        return '%s.urls' % self._guess_package()

    def get_create_instance_view(self):
        '''
        Return the view name for creating a new monitoring source.
        '''
        if self.create_instance_view is None:
            raise ImproperlyConfigured('subclasses of %s '
                    'must define the create_instance_view property or '
                    'reimplement get_create_instance_view()' %
                    self.__class__.__name__)
        return self.create_instance_view

    def get_model(self):
        '''
        Return the model class associated with this backend.
        '''
        if self.model is None:
            raise ImproperlyConfigured('subclasses of %s '
                    'must define the model property '
                    'or reimplement get_model()' %
                    self.__class__.__name__)
        if isinstance(self.model, six.string_types):
            model = get_model(self.model)
        else:
            model = self.model
        model.__backend__ = self
        return model

    def get_instances(self, active=None):
        '''
        Return a queryset containing model instances for this backend.

        The default is to return all instances. If *active* is given, only
        active or inactive instances are returned.
        '''
        model = self.get_model()
        qs = model.objects.all()
        if active is not None:
            qs = qs.filter(active=active)
        return qs


class MonitoringBackend(Backend):
    '''
    Base class for monitoring backends.
    '''


class AlertBackend(Backend):
    '''
    Base class for monitoring backends.
    '''

