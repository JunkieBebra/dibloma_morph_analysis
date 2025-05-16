from django.contrib import admin
from .models import Text, TextSection, Word, WordAnalysis, Dictionary, DictionaryEntry

admin.site.register(Text)
admin.site.register(TextSection)
admin.site.register(WordAnalysis)
admin.site.register(DictionaryEntry)

class WordAnalysisInline(admin.TabularInline):  # Можно использовать StackedInline для вертикального отображения
    model = WordAnalysis
    extra = 0  # Не показывать пустые дополнительные формы


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    inlines = [WordAnalysisInline]
    list_display = ('id', 'value', 'translation_value')
    search_fields = ['value']


class DictionaryEntryInline(admin.TabularInline):
    model = DictionaryEntry
    extra = 0
    autocomplete_fields = ['word']
    readonly_fields = ['word_text', 'translation', 'lemma', 'pos', 'added_at']
    fields = ['word', 'word_text', 'translation', 'lemma', 'pos', 'added_at']  # порядок отображения


    def word_text(self, obj):
        return obj.word.value
    word_text.short_description = "Слово"

    def translation(self, obj):
        return ", ".join(obj.word.translation_value or []) if obj.word.translation_value else "-"
    translation.short_description = "Перевод"

    def lemma(self, obj):
        return obj.word.analysis.first().lemma if obj.word.analysis.exists() else '-'
    lemma.short_description = "Лемма"

    def pos(self, obj):
        return obj.word.analysis.first().pos if obj.word.analysis.exists() else '-'
    pos.short_description = "Часть речи"


@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'created_at')
    inlines = [DictionaryEntryInline]
    search_fields = ['title']
    list_filter = ['status']
    ordering = ['-created_at']