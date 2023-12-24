import uuid
from rest_framework import urlpatterns

class IdConverter:
    regex = '[0-9a-z]+\-[0-9a-z]+\-[0-9a-z]+\-[0-9a-z]+'

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)

class UuidConverter(urlpatterns.RoutePattern):
    regex = 'uuid/(?P<id>[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'

    def __init__(self, callback, default_args=None, name=None):
        super().__init__(callback, default_args, name)

    def to_python(self, value):
        try:
            return uuid.UUID(value)
        except ValueError:
            return None

    def to_url(self, value):
        return str(value)