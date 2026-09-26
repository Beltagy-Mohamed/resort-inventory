from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone
import datetime


AVATAR_COLORS = [
    '#E74C3C', '#3498DB', '#2ECC71', '#9B59B6',
    '#F39C12', '#1ABC9C', '#E67E22', '#34495E',
    '#C0392B', '#2980B9', '#27AE60', '#8E44AD',
]


def random_color():
    return random.choice(AVATAR_COLORS)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=60, verbose_name='اسم العرض')
    avatar_color = models.CharField(max_length=7, default=random_color)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'ملف المستخدم'
        verbose_name_plural = 'ملفات المستخدمين'

    def __str__(self):
        return self.display_name

    @property
    def is_online(self):
        if not self.last_seen:
            return False
        return timezone.now() - self.last_seen < datetime.timedelta(minutes=1)

    @classmethod
    def get_or_create_for(cls, user):
        profile, created = cls.objects.get_or_create(
            user=user,
            defaults={
                'display_name': user.get_full_name() or user.username,
                'avatar_color': random_color(),
            }
        )
        return profile, created


class Room(models.Model):
    ROOM_TYPES = [('GROUP', 'قناة جماعية'), ('PRIVATE', 'خاص')]
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    name = models.CharField(max_length=100, blank=True)
    participants = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'غرفة'
        verbose_name_plural = 'غرف الدردشة'

    def __str__(self):
        if self.room_type == 'GROUP':
            return self.name or 'القناة العامة'
        return f'خاص #{self.pk}'

    @classmethod
    def get_or_create_private(cls, user1, user2):
        """Find or create a private room between two users."""
        rooms = cls.objects.filter(
            room_type='PRIVATE', participants=user1
        ).filter(participants=user2)
        if rooms.exists():
            return rooms.first()
        room = cls.objects.create(room_type='PRIVATE')
        room.participants.add(user1, user2)
        return room

    @classmethod
    def get_group_room(cls):
        """Get (or create) the single group channel."""
        room, _ = cls.objects.get_or_create(
            room_type='GROUP',
            defaults={'name': 'القناة العامة'}
        )
        return room

    def get_display_name_for(self, user):
        """Return room display name from a given user's perspective."""
        if self.room_type == 'GROUP':
            return self.name or 'القناة العامة'
        other = self.participants.exclude(pk=user.pk).first()
        if other:
            try:
                return other.profile.display_name
            except UserProfile.DoesNotExist:
                return other.username
        return 'محادثة خاصة'

    def get_other_user(self, user):
        """For private rooms, return the other participant."""
        return self.participants.exclude(pk=user.pk).first()

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count_for(self, user):
        """Count messages in this room that user hasn't read yet."""
        try:
            status = MessageReadStatus.objects.get(user=user, room=self)
            return self.messages.filter(
                created_at__gt=status.last_read_at
            ).exclude(sender=user).count()
        except MessageReadStatus.DoesNotExist:
            return self.messages.exclude(sender=user).count()


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['room', 'created_at'])]
        verbose_name = 'رسالة'
        verbose_name_plural = 'الرسائل'

    def __str__(self):
        return f'{self.sender} → {self.room}: {self.content[:40]}'

    def is_read_by_others(self):
        if self.room.room_type == 'GROUP':
            return False # Group read receipts are complex, ignore for now
        other_user = self.room.participants.exclude(pk=self.sender_id).first()
        if not other_user:
            return False
        try:
            status = MessageReadStatus.objects.get(user=other_user, room=self.room)
            return status.last_read_at >= self.created_at
        except MessageReadStatus.DoesNotExist:
            return False

    def to_dict(self, current_user=None):
        try:
            profile = self.sender.profile
            display_name = profile.display_name
            avatar_color = profile.avatar_color
        except UserProfile.DoesNotExist:
            display_name = self.sender.username
            avatar_color = '#3498DB'

        return {
            'id': self.pk,
            'sender_id': self.sender_id,
            'sender_name': display_name,
            'avatar_color': avatar_color,
            'content': self.content,
            'image_url': self.image.url if self.image else None,
            'is_mine': (self.sender_id == current_user.pk) if current_user else False,
            'created_at': self.created_at.strftime('%H:%M'),
            'created_at_full': self.created_at.isoformat(),
            'is_read': self.is_read_by_others(),
        }


class MessageReadStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_statuses')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='read_statuses')
    last_read_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'room')
        verbose_name = 'حالة القراءة'
        verbose_name_plural = 'حالات القراءة'
