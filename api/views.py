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
    authentication_classes = [TokenAuthentication]
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        sections = instance.sections.order_by('section_index')
        full_text = ''.join([section.content for section in sections])
        data = self.get_serializer(instance).data
        data['full_text'] = full_text
        return Response(data)

    @action(detail=True, methods=['get'], url_path='section/(?P<section_index>\\d+)')
    def get_section(self, request, pk=None, section_index=None):
        """
        Получить конкретную секцию текста по номеру.
        """
        try:
            section = TextSection.objects.get(text_id=pk, section_index=section_index)
            return Response({'section_index': section.section_index, 'content': section.content})
        except TextSection.DoesNotExist:
            return Response({'error': 'Секция не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='whole')
    def get_full_text(self, request, pk=None):
        """
        Получить весь текст, собранный из всех секций.
        """
        sections = TextSection.objects.filter(text_id=pk).order_by('section_index')
        full_text = ''.join([section.content for section in sections])
        return Response({'full_text': full_text})