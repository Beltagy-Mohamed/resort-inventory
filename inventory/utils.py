from django.conf import settings


def get_client_ip(request):
    """
    استخراج الـ IP الحقيقي للعميل بشكل آمن.

    إذا كان السيرفر خلف Reverse Proxy (Nginx)، أضف إلى settings.py:
        TRUSTED_PROXY_IPS = ['127.0.0.1']   # IP بتاع Nginx

    بدون هذا الإعداد، يُستخدم REMOTE_ADDR دائماً (آمن من Spoofing).
    """
    trusted_proxies = getattr(settings, "TRUSTED_PROXY_IPS", [])
    remote_addr = request.META.get("REMOTE_ADDR", "")

    if trusted_proxies and remote_addr in trusted_proxies:
        # الطلب جاي من Nginx — يمكن الوثوق بـ X-Forwarded-For
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if x_forwarded_for:
            # أول عنوان في السلسلة هو العميل الأصلي
            return x_forwarded_for.split(",")[0].strip()

    # الطلب مباشر أو من proxy غير موثوق — نستخدم REMOTE_ADDR فقط
    return remote_addr

from django.utils import timezone
from datetime import timedelta
import datetime

def get_period_date_range(period, start_date_str=None, end_date_str=None):
    now = timezone.now()
    if period == 'week':
        return now - timedelta(days=7), now
    elif period == 'month':
        return now - timedelta(days=30), now
    elif period == 'custom' and start_date_str and end_date_str:
        try:
            start_dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_dt = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            return timezone.make_aware(datetime.datetime.combine(start_dt, datetime.time.min)),                    timezone.make_aware(datetime.datetime.combine(end_dt, datetime.time.max))
        except ValueError:
            pass
    return None, None
