from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.shortcuts import redirect, render

from ..forms import SystemSettingsForm
from ..models import SystemSettings


@user_passes_test(lambda u: u.is_superuser)
def system_settings(request):

    settings_obj = SystemSettings.load()

    if request.method == "POST":

        form = SystemSettingsForm(
            request.POST,
            instance=settings_obj
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "تم حفظ الإعدادات بنجاح."
            )

            return redirect("system_settings")

    else:

        form = SystemSettingsForm(instance=settings_obj)

    return render(
        request,
        "settings/edit.html",
        {
            "form": form
        }
    )
