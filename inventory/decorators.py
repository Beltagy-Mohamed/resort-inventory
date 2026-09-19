from django.http import Http404
from functools import wraps
from django.contrib.auth.models import Group
from inventory.models import LeadershipAccessConfig


def is_the_leader(user) -> bool:
    """True إذا كان المستخدم هو حامل صلاحية القيادة الحالي أو مدير نظام أو في مجموعة القائد."""
    if not user.is_authenticated:
        return False
        
    # Superusers see everything
    if user.is_superuser:
        return True
        
    # Check if user is in 'Leader' group (from UI checkbox)
    if user.groups.filter(name="Leader").exists():
        return True
        
    # Check singleton table just in case
    config = LeadershipAccessConfig.objects.select_related("holder").first()
    return config is not None and config.holder_id == user.id


def is_leader_staff(user) -> bool:
    """True إذا كان المستخدم عضواً في مجموعة LeaderStaff."""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name="LeaderStaff").exists()


def is_leader_or_staff(user) -> bool:
    """True إذا كان المستخدم إما القائد أو أحد موظفي القائد أو مدير نظام."""
    return is_the_leader(user) or is_leader_staff(user)


def leadership_required(view_func):
    """
    يسمح بالوصول للقائد (حامل الصلاحية) أو مدير النظام.
    يُرجع 404 (لا 403).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_the_leader(request.user):
            raise Http404()
        return view_func(request, *args, **kwargs)
    return wrapper


def leader_or_leaderstaff_required(view_func):
    """
    يسمح بالوصول للقائد أو موظفي القائد أو مدير النظام.
    يُرجع 404 (لا 403).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_leader_or_staff(request.user):
            raise Http404()
        return view_func(request, *args, **kwargs)
    return wrapper
