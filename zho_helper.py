import re
from opencc_rs import OpenCC


def check_text_code(text):
    if not text:
        return 0
    # return OpenCC().zho_check(text)
    strip_text = re.sub(r'[\WA-Za-z0-9_]', "", text)
    test_text = strip_text if len(strip_text) < 30 else strip_text[0:30]
    if test_text != OpenCC("t2s").convert(test_text):
        return 1
    else:
        if test_text != OpenCC("s2t").convert(test_text):
            return 2
        else:
            return 0


def convert_punctuation(input_text, config):
    # Declare a dictionary to store the characters and their mappings
    s2t_punctuation = {
        '“': '「',
        '”': '」',
        '‘': '『',
        '’': '』'
    }
    if config[0] == "s":
        mapping = s2t_punctuation
    else:
        mapping = {v: k for k, v in s2t_punctuation.items()}

    # Correct and safe way to build the pattern:
    escaped_chars = [re.escape(char) for char in mapping.keys()]
    pattern = f"[{''.join(escaped_chars)}]"

    output_text = re.sub(pattern, lambda m: mapping[m.group(0)], input_text)
    return output_text
