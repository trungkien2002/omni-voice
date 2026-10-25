"""Local, explicit speaker-label parsing. Unlabelled instructions remain narration."""
from dataclasses import dataclass, field
import re
import unicodedata

NARRATOR = '__narrator__'

@dataclass
class Turn:
    role: str
    text: str
    line: int

@dataclass
class Script:
    turns: list[Turn] = field(default_factory=list)
    roles: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

def role_name(role):
    return 'Lời dẫn' if role == NARRATOR else role

def parse_dialogue(text):
    """Names come from line labels, never from the introduction or guessed dialogue."""
    result = Script()
    names = {}
    continued = False
    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continued = False
            continue
        match = re.match(r'^(?:[-–—•]\s*)?([^:：\n]{1,48})\s*[:：]\s*(.*)$', line)
        label = re.sub(r'\s+', ' ', match[1]).strip() if match else ''
        valid_label = bool(label) and len(label.split()) <= 5 and bool(re.search(r'[^\W\d_]', label))
        valid_label = valid_label and not re.search(r'[.!?;<>/\\]', label)
        reserved = re.match(r'^(?:part\b|section\b|question\b|note\b|listen\b|now listen\b|hướng dẫn\b)', label, re.I)
        if valid_label and not reserved:
            canonical = unicodedata.normalize('NFC', label).casefold()
            role = names.setdefault(canonical, unicodedata.normalize('NFC', label))
            if role not in result.roles:
                result.roles.append(role)
            body = match[2].strip()
            if body:
                result.turns.append(Turn(role, body, line_no))
            else:
                result.warnings.append(f'Dòng {line_no}: vai {role} chưa có lời thoại.')
            continued = bool(body)
        elif (raw[:1].isspace() and continued and result.turns
              and result.turns[-1].role != NARRATOR
              and not re.match(r'^(?:now listen|part\b|section\b)', line, re.I)):
            result.turns[-1].text += '\n' + line
        else:
            if NARRATOR not in result.roles:
                result.roles.insert(0, NARRATOR)
            if result.turns and result.turns[-1].role == NARRATOR and continued:
                result.turns[-1].text += '\n' + line
            else:
                result.turns.append(Turn(NARRATOR, line, line_no))
            continued = True
    if not names and result.turns:
        result.warnings.append('Chưa thấy nhãn tên nhân vật. Các câu này sẽ đọc bằng giọng Lời dẫn; dùng dạng Lan: lời thoại để tách vai.')
    # Detect a common source-text typo without rewriting or inventing a role.
    introduction = re.search(r'conversation between\s+([\wÀ-ỹ -]+?)\s+and\s+([\wÀ-ỹ -]+?)[.!?\n]', text, re.I)
    if introduction and names:
        claimed = {unicodedata.normalize('NFC', n.strip()).casefold() for n in introduction.groups()}
        actual = set(names)
        if claimed != actual:
            result.warnings.append('Tên trong lời hướng dẫn khác nhãn thoại. Vai được nhận diện theo nhãn; lời hướng dẫn vẫn được giữ nguyên.')
    return result
