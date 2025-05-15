from django.contrib import admin
from .models import Text, TextSection, Dictionary, Word, WordAnalysis

admin.site.register(Text)
admin.site.register(TextSection)
admin.site.register(Dictionary)
admin.site.register(Word)
admin.site.register(WordAnalysis)