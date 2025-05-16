from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Text, TextSection, Word, Dictionary, DictionaryEntry
from .serializers import TextSerializer
from utils.text_splitter import split_text_into_sections
from .permissions import IsOwnerOrAdmin
from rest_framework.permissions import IsAuthenticated
from morphology_analysis.pipeline import analyze_section
from api.serializers import WordSerializer, DictionarySerializer, DictionaryEntrySerializer

from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

from datetime import datetime
import csv



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
    

    @action(detail=True, methods=['get'], url_path='section/(?P<section_index>[^/.]+)/words')
    def section_words(self, request, pk=None, section_index=None):
        """
        Получить cловарь всех слов в секции текста.
        """
        try:
            text = self.get_object()
            section = text.sections.get(section_index=section_index)
        except:
            return Response({"error": "Секция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        words = section.words.all().prefetch_related('analysis')
        serializer = WordSerializer(words, many=True)
        return Response(serializer.data)
    

    @action(detail=True, methods=['get'], url_path='whole')
    def get_full_text(self, request, pk=None):
        """
        Получить весь текст, собранный из всех секций.
        """
        sections = TextSection.objects.filter(text_id=pk).order_by('section_index')
        full_text = ''.join([section.content for section in sections])
        return Response({'full_text': full_text})
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        text = self.get_object()
        sections = text.sections.all()
        total = sections.count()

        for section in sections:
            analyze_section(section)

        response = {"message": f"Морфоанализ {total} секции завершён"
                    } if total == 1 else {"message": f"Морфоанализ {total} секций завершён"}
        return Response(
            response,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], url_path='section/(?P<section_index>[^/.]+)/words')
    def section_words(self, request, pk=None, section_index=None):
        try:
            text = self.get_object()
            section = text.sections.get(section_index=section_index)
        except:
            return Response({"error": "Секция не найдена"}, status=status.HTTP_404_NOT_FOUND)

        words = section.words.all().prefetch_related('analysis')

        # Выбор сериализатора
        detailed = request.query_params.get('detailed') == 'true'
        serializer_class = WordSerializer if detailed else WordSummarySerializer

        serializer = serializer_class(words, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def words(self, request, pk=None):
        text = self.get_object()
        words = Word.objects.filter(section__text=text).distinct().prefetch_related('analysis')

        detailed = request.query_params.get('detailed') == 'true'
        serializer_class = WordSerializer if detailed else WordSummarySerializer

        serializer = serializer_class(words, many=True)
        return Response(serializer.data)
    
    
class WordDetailAPIView(RetrieveAPIView):
    queryset = Word.objects.prefetch_related('analysis')
    serializer_class = WordSerializer



class DictionaryViewSet(viewsets.ModelViewSet):
    serializer_class = DictionarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dictionary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, title=self.request.data.get('title'), status=self.request.data.get('status'))

    @action(detail=True, methods=['get'], url_path='export/pdf')
    def export_pdf(self, request, pk=None):
        dictionary = self.get_object()

        if dictionary.user != request.user:
            return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

        entries = dictionary.entries.select_related('word').prefetch_related('word__analysis').all()

        html_string = render_to_string("dictionary-export-template.html", {
            "dictionary": dictionary,
            "entries": entries,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

        pdf = HTML(string=html_string).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="dictionary_{dictionary.id}.pdf"'
        return response
    
    @action(detail=True, methods=['get'], url_path='export/csv')
    def export_csv(self, request, pk=None):
        dictionary = self.get_object()

        if dictionary.user != request.user:
            return Response({"error": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

        entries = dictionary.entries.select_related('word').prefetch_related('word__analysis').all()

        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="dictionary_{dictionary.id}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Слово', 'Перевод', 'Лемма', 'Часть речи'])

        for entry in entries:
            word = entry.word
            analysis = word.analysis.first() if word.analysis.exists() else None
            writer.writerow([
                word.value,
                ', '.join(word.translation_value or []) if word.translation_value else '',
                analysis.lemma if analysis else '',
                analysis.pos if analysis else ''
            ])

        return response
    

class DictionaryEntryViewSet(viewsets.ModelViewSet):
    serializer_class = DictionaryEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DictionaryEntry.objects.filter(dictionary__user=self.request.user)

    def perform_create(self, serializer):
        dictionary_id = self.request.data.get('dictionary_id')
        try:
            dictionary = Dictionary.objects.get(id=dictionary_id, user=self.request.user)
        except Dictionary.DoesNotExist:
            return Response({"error": "Словарь не найден или не принадлежит пользователю"})

        serializer.save(dictionary=dictionary)