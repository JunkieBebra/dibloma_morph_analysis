from api.models import TextSection, Word, WordAnalysis
from morphology_analysis.analyzer import analyze_text
from django.db import transaction

@transaction.atomic
def analyze_section(section: TextSection):
    """
    Анализирует одну секцию текста. Кэширует результаты:
    - если слово уже есть — добавляется связь с секцией;
    - если нет — создаётся новое слово и разбор.
    """
    words_data = analyze_text(section.content)

    for word_info in words_data:
        value = word_info["text"]
        lemma = word_info["lemma"]
        pos = word_info["pos"]
        morph = word_info["morph"]

        # 1. Попробуем найти уже разобранное слово
        word = Word.objects.filter(value=value).first()

        if word:
            # 2. Уже есть — добавим секцию, если не связано
            word.section.add(section)
        else:
            # 3. Создаём новое слово и разбор
            word = Word.objects.create(value=value)
            word.section.add(section)

            WordAnalysis.objects.create(
                word=word,
                lemma=lemma,
                pos=pos,
                morph=morph
            )
