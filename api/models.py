from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Text(models.Model):
    STATUS_CHOICES = [
        ('opened', 'Открыт для других пользователей'),
        ('closed', 'Доступен только автору'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='texts')
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='closed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"
    

class Dictionary(models.Model):
    STATUS_CHOICES = [
        ('opened', 'Открыт для других пользователей'),
        ('closed', 'Доступен только автору'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dictionaries')
    words = models.ManyToManyField('Word', related_name='dictionaries')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='closed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.user.username})"
    

class Word(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(max_length=255)
    morph_analysis = models.JSONField()
    translation_value = models.JSONField()
