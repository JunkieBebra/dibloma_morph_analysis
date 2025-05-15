import spacy

nlp = spacy.load("en_core_web_sm")

def analyze_text(text):
    doc = nlp(text)
    return [{
        "text": token.text,
        "lemma": token.lemma_,
        "pos": token.pos_,
        "morph": token.morph.to_dict()
    } for token in doc if token.is_alpha]