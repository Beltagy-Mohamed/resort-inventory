import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Max

from .models import Message, MessageReadStatus, Room, UserProfile


def _get_or_create_profile(user):
    profile, created = UserProfile.get_or_create_for(user)
    return profile, created


@login_required
def chat_home(request):
    profile, is_new = _get_or_create_profile(request.user)

    # Redirect to set name on first visit
    if is_new or not profile.display_name:
        return redirect('chat_set_name')

    group_room = Room.get_group_room()
    group_room.participants.add(request.user)  # ensure user is in group room

    # Get all private rooms for this user
    private_rooms = Room.objects.filter(
        room_type='PRIVATE', participants=request.user
    ).prefetch_related('participants', 'participants__profile')

    # Annotate with last message time for ordering
    rooms_data = []

    # Group room first
    last_msg = group_room.get_last_message()
    rooms_data.append({
        'room': group_room,
        'display_name': 'القناة العامة 📢',
        'last_message': last_msg,
        'unread': group_room.unread_count_for(request.user),
        'avatar_color': '#3498DB',
        'avatar_char': '📢',
        'is_group': True,
    })

    for room in private_rooms:
        other = room.get_other_user(request.user)
        if not other:
            continue
        try:
            other_profile = other.profile
            display_name = other_profile.display_name
            avatar_color = other_profile.avatar_color
        except UserProfile.DoesNotExist:
            display_name = other.username
            avatar_color = '#95a5a6'

        last_msg = room.get_last_message()
        rooms_data.append({
            'room': room,
            'display_name': display_name,
            'last_message': last_msg,
            'unread': room.unread_count_for(request.user),
            'avatar_color': avatar_color,
            'avatar_char': display_name[0] if display_name else '?',
            'is_group': False,
        })

    # Sort by last message time (newest first), group always first
    private_part = [r for r in rooms_data if not r['is_group']]
    private_part.sort(
        key=lambda x: x['last_message'].created_at if x['last_message'] else timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )
    rooms_data = rooms_data[:1] + private_part

    # All users for "new chat" modal
    all_users = User.objects.exclude(pk=request.user.pk).filter(is_active=True).select_related('profile')

    context = {
        'rooms_data': rooms_data,
        'all_users': all_users,
        'profile': profile,
    }
    return render(request, 'chat/home.html', context)


@login_required
def room_view(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    profile, _ = _get_or_create_profile(request.user)

    # Access control: group rooms are open to all, private rooms only to participants
    if room.room_type == 'PRIVATE' and not room.participants.filter(pk=request.user.pk).exists():
        return redirect('chat_home')

    # Add user to group room if not already
    if room.room_type == 'GROUP':
        room.participants.add(request.user)

    # Mark as read
    MessageReadStatus.objects.update_or_create(
        user=request.user, room=room,
        defaults={'last_read_at': timezone.now()}
    )

    # Load last 50 messages
    messages_qs = room.messages.select_related('sender', 'sender__profile').order_by('-created_at')[:50]
    messages_list = list(reversed(messages_qs))

    # Room display name
    is_online = False
    if room.room_type == 'GROUP':
        room_name = 'القناة العامة 📢'
        other_user = None
    else:
        other_user = room.get_other_user(request.user)
        room_name = room.get_display_name_for(request.user)
        if other_user:
            try:
                is_online = other_user.profile.is_online
            except:
                pass

    context = {
        'room': room,
        'room_name': room_name,
        'messages_list': messages_list,
        'profile': profile,
        'other_user': other_user,
        'is_online': is_online,
        'last_timestamp': messages_list[-1].created_at.isoformat() if messages_list else '',
    }
    return render(request, 'chat/room.html', context)


@login_required
def start_private(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    if other_user == request.user:
        return redirect('chat_home')
    room = Room.get_or_create_private(request.user, other_user)
    return redirect('chat_room', room_id=room.pk)


@login_required
@require_http_methods(['GET', 'POST'])
def api_messages(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    # Access control
    if room.room_type == 'PRIVATE' and not room.participants.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method == 'POST':
        content = ''
        image = None
        if request.content_type.startswith('multipart/form-data'):
            content = request.POST.get('content', '').strip()
            image = request.FILES.get('image')
        else:
            try:
                data = json.loads(request.body)
                content = data.get('content', '').strip()
            except (json.JSONDecodeError, KeyError):
                pass

        if not content and not image:
            return JsonResponse({'error': 'Empty message'}, status=400)

        msg = Message.objects.create(room=room, sender=request.user, content=content, image=image)

        # Update read status for sender
        MessageReadStatus.objects.update_or_create(
            user=request.user, room=room,
            defaults={'last_read_at': timezone.now()}
        )

        return JsonResponse({'message': msg.to_dict(request.user)}, status=201)

    # GET: return messages after a timestamp
    after = request.GET.get('after', '')
    try:
        from datetime import datetime
        after_dt = datetime.fromisoformat(after.replace('Z', '+00:00')) if after else None
    except (ValueError, AttributeError):
        after_dt = None

    qs = room.messages.select_related('sender', 'sender__profile')
    if after_dt:
        qs = qs.filter(created_at__gt=after_dt)
    else:
        qs = qs.order_by('-created_at')[:50]
        qs = list(reversed(qs))

    # Update read status and last_seen
    if request.user.is_authenticated:
        profile, _ = _get_or_create_profile(request.user)
        profile.last_seen = timezone.now()
        profile.save()

    if qs:
        MessageReadStatus.objects.update_or_create(
            user=request.user, room=room,
            defaults={'last_read_at': timezone.now()}
        )

    return JsonResponse({
        'messages': [m.to_dict(request.user) for m in qs]
    })


@login_required
def api_unread_count(request):
    """Total unread messages across all rooms for the notification badge."""
    total = 0
    user_rooms = Room.objects.filter(participants=request.user)
    for room in user_rooms:
        total += room.unread_count_for(request.user)
    return JsonResponse({'unread': total})


@login_required
def get_users_list(request):
    users = User.objects.exclude(pk=request.user.pk).filter(is_active=True)
    data = []
    for u in users:
        try:
            display_name = u.profile.display_name
            color = u.profile.avatar_color
        except UserProfile.DoesNotExist:
            display_name = u.get_full_name() or u.username
            color = '#3498DB'
        data.append({
            'id': u.pk,
            'display_name': display_name,
            'avatar_color': color,
        })
    return JsonResponse({'users': data})


@login_required
@require_http_methods(['GET', 'POST'])
def set_display_name(request):
    profile, _ = _get_or_create_profile(request.user)
    if request.method == 'POST':
        name = request.POST.get('display_name', '').strip()
        if name:
            profile.display_name = name
            profile.save()
            return redirect('chat_home')
    return render(request, 'chat/set_name.html', {'profile': profile})
