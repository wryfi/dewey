from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedRelatedField

from hosts.models import Host, Cluster
from hardware.models import Server

class HyperlinkedGenericRelatedField(HyperlinkedRelatedField):
    """
    This class removes the requirement from HyperlinkRelatedField that view_name
    must be set during init, allowing us to subclass this class and dynamically
    handle the view name in the to_representation() and to_internal_value() methods.
    """
    def __init__(self, view_name=None, **kwargs):
        if view_name is not None:
            self.view_name = view_name
        self.lookup_field = kwargs.pop('lookup_field', self.lookup_field)
        self.lookup_url_kwarg = kwargs.pop('lookup_url_kwarg', self.lookup_field)
        self.format = kwargs.pop('format', None)

        # We include this simply for dependency injection in tests.
        # We can't add it as a class attributes or it would expect an
        # implicit `self` argument to be passed.
        self.reverse = reverse

        super(HyperlinkedRelatedField, self).__init__(**kwargs)

    def to_representation(self, value):
        raise NotImplementedError

    def to_internal_value(self, data):
        raise NotImplementedError