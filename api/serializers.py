from rest_framework import serializers
from .models import Text

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = '__all__'  # Включаем все поля
        read_only_fields = ['user']  # Поле user только для чтения
