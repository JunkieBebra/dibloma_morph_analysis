from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from .models import Text, TextSection
from .serializers import TextSerializer
from utils.text_splitter import split_text_into_sections
from .permissions import IsOwnerOrAdmin
from rest_framework.permissions import IsAuthenticated

class TextViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]  # Указываем аутентификацию по токену
    permission_classes = [IsAuthenticated]
    queryset = Text.objects.all()
    serializer_class = TextSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Text.objects.all()
        return Text.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        text_obj = serializer.save(user=self.request.user)

        uploaded_file = self.request.FILES.get('file', None)
        if uploaded_file:
            full_text = uploaded_file.read().decode('utf-8')
        else:
            full_text = self.request.data.get('content', '')
        if not full_text:
            raise ValueError("Поле 'content' или 'file' не может быть пустым")

        sections = split_text_into_sections(full_text)
        for i, section in enumerate(sections):
            TextSection.objects.create(
                text=text_obj,
                section_index=i,
                content=section
            )