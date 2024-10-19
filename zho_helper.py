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
    s2t_punctuation_chars = {
        '“': '「',
        '”': '」',
        '‘': '『',
        '’': '』'
    }
    # Use the join method to create the regular expression patterns
    if config[0] == "s":
        pattern = f"[{''.join(s2t_punctuation_chars.keys())}]"  # "[“”‘’]"
        output_text = re.sub(
            pattern, lambda m: s2t_punctuation_chars[m.group(0)], input_text)
    else:
        # Use the dict comprehension to reverse the dictionary
        t2s_punctuation_chars = {v: k for k, v in s2t_punctuation_chars.items()}
        pattern = f"[{''.join(t2s_punctuation_chars.keys())}]"  # "[「」『』]"
        output_text = re.sub(
            pattern, lambda m: t2s_punctuation_chars[m.group(0)], input_text)

    return output_text