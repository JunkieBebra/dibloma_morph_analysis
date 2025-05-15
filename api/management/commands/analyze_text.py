from django.core.management.base import BaseCommand
from api.models import Text
from morphology_analysis.pipeline import analyze_section

class Command(BaseCommand):
    help = 'Выполняет морфологический анализ текста по его ID'

    def add_arguments(self, parser):
        parser.add_argument('text_id', type=int, help='ID текста для анализа')

    def handle(self, *args, **options):
        text_id = options['text_id']

        try:
            text = Text.objects.get(id=text_id)
        except Text.DoesNotExist:
            self.stderr.write(f"Текст с id={text_id} не найден.")
            return

        sections = text.sections.all()
        self.stdout.write(f"Найдено {sections.count()} секций. Начинаем анализ...")

        for section in sections:
            analyze_section(section)
            self.stdout.write(f"Разобрана секция {section.section_index}")

        self.stdout.write(self.style.SUCCESS(f"Анализ текста '{text.title}' (ID={text_id}) завершён."))
