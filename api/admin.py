from django.contrib import admin
from .models import Text, TextSection, Dictionary, Word, WordAnalysis

admin.site.register(Text)
admin.site.register(TextSection)
admin.site.register(Dictionary)
admin.site.register(WordAnalysis)

class WordAnalysisInline(admin.TabularInline):  # Можно использовать StackedInline для вертикального отображения
    model = WordAnalysis
    extra = 0  # Не показывать пустые дополнительные формы

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    inlines = [WordAnalysisInline]
    list_display = ('id', 'value', 'translation_value')