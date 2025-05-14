from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Text(models.Model):
    STATUS_CHOICES = [
        ('opened', 'Открыт для других пользователей'),
        ('closed', 'Закрыт для других пользователей'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True, default='Unknown')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='texts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='closed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author} ({self.user.username} added at {self.created_at})"
    
    def get_sections(self):
        return self.sections.all()
    

class TextSection(models.Model):
    text = models.ForeignKey(Text, on_delete=models.CASCADE, related_name='sections')
    section_index = models.PositiveIntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Section {self.section_index} of {self.text.title} ({self.text.user.username})"

    class Meta:
        unique_together = ('text', 'section_index')
        ordering = ['section_index']
    

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
