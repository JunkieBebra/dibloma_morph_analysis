from api.models import TextSection, Word, WordAnalysis
from morphology_analysis.analyzer import analyze_text
from django.db import transaction
from morphology_analysis.translation import get_translations

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

        word = Word.objects.filter(value=value).first()

        if word:
            word.section.add(section)
        else:
            word = Word.objects.create(
                value=value,
                translation_value=get_translations(lemma)
            )
            word.section.add(section)

            WordAnalysis.objects.create(
                word=word,
                lemma=lemma,
                pos=pos,
                morph=morph
            )
