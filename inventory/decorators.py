from django.http import Http404
from functools import wraps
from inventory.models import LeadershipAccessConfig

def is_the_leader(user) -> bool:
    if not user.is_authenticated:
        return False
    config = LeadershipAccessConfig.objects.select_related("holder").first()
    return config is not None and config.holder_id == user.id

def leadership_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_the_leader(request.user):
            raise Http404()
        return view_func(request, *args, **kwargs)
    return wrapper
