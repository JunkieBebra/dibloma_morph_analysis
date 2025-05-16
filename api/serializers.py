from rest_framework import serializers
from .models import Text, WordAnalysis, Word, Dictionary
from morphology_analysis.morph_utils import translate_pos, translate_morph

class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        fields = '__all__'
        read_only_fields = ['user']


class WordAnalysisSerializer(serializers.ModelSerializer):
    translated_pos = serializers.SerializerMethodField()
    translated_morph = serializers.SerializerMethodField()

    class Meta:
        model = WordAnalysis
        fields = ['lemma', 'pos', 'morph', 'translated_pos', 'translated_morph']

    def get_translated_pos(self, obj):
        return translate_pos(obj.pos)

    def get_translated_morph(self, obj):
        return translate_morph(obj.morph)
    

class WordSerializer(serializers.ModelSerializer):
    analysis = WordAnalysisSerializer(read_only=True, many=True)
    section_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
        source='section'
    )

    class Meta:
        model = Word
        fields = ['id', 'value', 'translation_value', 'analysis', 'section_ids']


class WordSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = ['id', 'value']


class DictionarySerializer(serializers.ModelSerializer):
    word = WordSerializer(read_only=True)
    word_id = serializers.PrimaryKeyRelatedField(
        queryset=Word.objects.all(), write_only=True, source='word'
    )

    class Meta:
        model = Dictionary
        fields = ['id', 'word', 'word_id', 'added_at']