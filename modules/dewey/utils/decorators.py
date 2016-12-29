from django.http import HttpResponseRedirect
from django.contrib import messages

from environments.models import Secret, Safe


class SafeAccessRequired(object):
    """
    This decorator determines whether a user has access to a specific safe.
    Access is based on membership in a group that matches the name of the safe's
    environment. The decorator takes a single parameter, which is the name of the lookup
    parameter for the safe from a URL pattern.
    """
    def __init__(self, urlparam):
        self.urlparam = urlparam

    def __call__(self, view):
        def decorated(request, *args, **kwargs):
            user_groups = [group.name for group in request.user.groups.all()]
            safe = Safe.objects.get(name=kwargs.get(self.urlparam))
            if safe.environment_name != 'all':
                if not request.user.is_superuser and safe.environment_name not in user_groups:
                    message = 'You don\'t have access to safes in the {} environment.'.format(safe.environment_name)
                    messages.add_message(request, messages.ERROR, message)
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            return view(request, *args, **kwargs)
        return decorated

