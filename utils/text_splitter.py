def split_text_into_sections(text: str, max_chars: int = 5000) -> list[str]:
    sections = []
    i = 0
    length = len(text)

    while i < length:
        end = i + max_chars
        if end >= length:
            sections.append(text[i:].strip())
            break

        while end > i and text[end] not in [' ', '\n', '\t']:
            end -= 1
            
        if end == i:
            end = i + max_chars

        section = text[i:end].strip()
        sections.append(section)
        i = end

    return sections