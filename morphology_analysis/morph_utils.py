from morphology_analysis.constants import POS_TAGS, MORPH_TRANSLATIONS

def translate_pos(pos_code):
    return POS_TAGS.get(pos_code, pos_code)

def translate_morph(morph_dict):
    translated = {}
    for k, v in morph_dict.items():
        group = MORPH_TRANSLATIONS.get(k)
        if group:
            translated[k] = group.get(v, v)
        else:
            translated[k] = v
    return translated