import os.path
import re
import tkinter as tk  # GUI
import jieba  # Segmentor module
import pyperclip as pc  # Clipboard module
from opencc import OpenCC  # use module: pip install -u opencc-python-reimplemented
from tkinter.filedialog import askopenfilename


def paste_input(source_textbox, source_charcode_label, config_option, source_charcount_label, filename_label):
    text = pc.paste()
    source_textbox.delete("1.0", tk.END)
    source_textbox.insert("1.0", text)

    strip_text = re.sub(r'[\\WA-Za-z0-9_]', "", text)
    test_text = strip_text if len(strip_text) < 30 else strip_text[0:30]
    update_source_info(check_textcode(test_text),
                       source_charcode_label, config_option)

    source_charcount_label.config(text=f"( {len(text):,} Chars )")
    filename_label.config(text="")


def update_source_info(textcode, source_charcode_label, config_option):
    match textcode:
        case 1:
            source_charcode_label.config(text="zh-Hant (繁体)")
            config_option.set(value="tw2s")
        case 2:
            source_charcode_label.config(text="zh-Hans (简体)")
            config_option.set(value="s2tw")
        case _:
            source_charcode_label.config(text="Non-zh (其它)")


def copy_output(destination_textbox):
    pc.copy(destination_textbox.get("1.0", 'end-2c'))


def open_file(source_textbox, source_charcode_label, config_option, source_charcount_label, filename_label):
    filename = askopenfilename(initialdir="./", title="Open File", filetypes=(
        ("Text Files", "*.txt"), ("Subtitle Files", "*.srt;*.vtt;*.ass;*.ttml2;*.xml"), ("All Files", "*.*")))

    if not filename:
        return

    with open(filename, "r", encoding="utf-8") as f:
        contents = f.read()

    source_textbox.delete("1.0", tk.END)
    source_textbox.insert("1.0", contents)

    strip_text = re.sub(r'[\\WA-Za-z0-9_]', "", contents)
    test_text = strip_text if len(strip_text) < 30 else strip_text[0:30]
    update_source_info(check_textcode(test_text),
                       source_charcode_label, config_option)

    source_charcount_label.config(text=f"( {len(contents):,} Chars )")
    filename_label.config(text=os.path.basename(filename))


def convert(source_textbox, config_option, region_config_option, zhtw_option, punctuation_option, destination_textbox,
            source_charcode_label, destination_charcode_label):
    output_text = ""
    input_text = source_textbox.get("1.0", tk.END)

    if input_text == "\n":
        return

    if config_option.get() == "jieba":
        segment_list = jieba.cut(input_text)
        output_text = "/".join(segment_list)
    else:
        match region_config_option.get():
            case "std":
                converter = OpenCC(config_option.get().replace(
                    "tw", "t"))
                output_text = converter.convert(input_text)
            case "zhtw":
                converter = OpenCC(config_option.get() +
                                   "p" if zhtw_option.get() else config_option.get())
                output_text = converter.convert(input_text)
            case "hk":
                converter = OpenCC(config_option.get().replace(
                    "tw", "hk"))
                output_text = converter.convert(input_text)

    if punctuation_option.get() and "jieba" not in config_option.get():
        output_text = convert_punctuation(output_text, config_option.get())

    destination_textbox.delete("1.0", tk.END)
    destination_textbox.insert("1.0", output_text)

    if config_option.get() != "jieba" and "Non-zh" not in source_charcode_label.cget("text"):
        destination_charcode_label.config(
            text="zh-Hant (繁体)" if config_option.get() == "s2tw" else "zh-Hans (简体)")
    else:
        destination_charcode_label.config(
            text=source_charcode_label.cget("text"))


def check_textcode(text):
    converted_text = OpenCC("t2s").convert(text)
    if converted_text != text:
        return 1
    elif OpenCC("s2t").convert(converted_text) != text:
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


def std_hk_select(zhtw_option):
    zhtw_option.set(0)


def zhtw_select(zhtw_option):
    zhtw_option.set(1)


def main():
    # === Main Window === #
    window = tk.Tk()
    window.title("Hans <-> Hant Converter")

    frame = tk.Frame(window)
    frame.pack()

    config_labelframe = tk.LabelFrame(frame, text="Configuration")
    config_labelframe.grid(row=0, column=0, padx=20, pady=5, sticky="news")
    config_option = tk.StringVar(value="tw2s")
    region_config_option = tk.StringVar(value="zhtw")
    zhtw_option = tk.IntVar(value=1)
    punctuation_option = tk.IntVar(value=1)

    t2s_radiobutton = tk.Radiobutton(
        config_labelframe, text="zh-Hant (繁体) to zh-Hans (简体)", padx=20, pady=5, value="tw2s",
        variable=config_option,
        font="Arial 12")
    s2t_radiobutton = tk.Radiobutton(
        config_labelframe, text="zh-Hans (简体) to zh-hant (繁体)", padx=20, pady=5, value="s2tw",
        variable=config_option,
        font="Arial 12")
    jieba_radiobutton = tk.Radiobutton(config_labelframe, text="Words Segmentor (拆词)",
                                       padx=20, pady=5, value="jieba", variable=config_option, font="Arial 12")

    std_radiobutton = tk.Radiobutton(config_labelframe, text="Standard (标准简繁)",
                                     variable=region_config_option, value="std",
                                     command=lambda: std_hk_select(zhtw_option), font="Arial 10")
    zhtw_radiobutton = tk.Radiobutton(config_labelframe, text="Mainland/Taiwan (中台简繁)",
                                      variable=region_config_option, value="zhtw",
                                      command=lambda: zhtw_select(zhtw_option), font="Arial 10")
    hk_radiobutton = tk.Radiobutton(config_labelframe, text="Hong Kong (香港简繁)",
                                    variable=region_config_option, value="hk",
                                    command=lambda: std_hk_select(zhtw_option), font="Arial 10")

    zhtw_checkbutton = tk.Checkbutton(
        config_labelframe, text="ZH/TW Idioms (中台惯用语)", variable=zhtw_option, font="Arial 10")
    punctuation_checkbutton = tk.Checkbutton(
        config_labelframe, text="Punctuation (标点符号)", variable=punctuation_option, font="Arial 10")

    t2s_radiobutton.grid(row=0, column=0)
    s2t_radiobutton.grid(row=0, column=1)
    jieba_radiobutton.grid(row=0, column=2)
    std_radiobutton.grid(row=2, column=0)
    zhtw_radiobutton.grid(row=2, column=1)
    hk_radiobutton.grid(row=2, column=2)
    zhtw_checkbutton.grid(row=3, column=1)
    punctuation_checkbutton.grid(row=3, column=2)

    content_labelframe = tk.LabelFrame(frame, text="Contents")
    content_labelframe.grid(row=1, column=0, padx=20, pady=5, sticky="news")

    source_textbox = tk.Text(content_labelframe, width=50,
                             height=25, font=("Consolas", 11))
    source_textbox.grid(row=0, column=0, padx=(10, 0), pady=5)
    source_scrollbar = tk.Scrollbar(
        content_labelframe, command=source_textbox.yview)
    source_scrollbar.grid(row=0, column=1, sticky="news")
    source_textbox['yscrollcommand'] = source_scrollbar.set

    destination_textbox = tk.Text(
        content_labelframe, width=50, height=25, font=("Consolas", 11))
    destination_textbox.grid(row=0, column=2, padx=(10, 0), pady=5)
    destination_scrollbar = tk.Scrollbar(
        content_labelframe, command=destination_textbox.yview)
    destination_scrollbar.grid(row=0, column=3, sticky="news")
    destination_textbox['yscrollcommand'] = destination_scrollbar.set

    source_labelframe = tk.LabelFrame(content_labelframe)
    destination_labelframe = tk.LabelFrame(content_labelframe)
    source_labelframe.grid(row=1, column=0, sticky="news",
                           padx=10, pady=5, columnspan=2)
    destination_labelframe.grid(
        row=1, column=2, sticky="news", padx=10, pady=5, columnspan=2)
    source_label = tk.Label(source_labelframe, text="Source")
    destination_label = tk.Label(destination_labelframe, text="Destination")
    source_label.grid(row=0, column=0, padx=5, pady=5)
    destination_label.grid(row=0, column=0, padx=5, pady=5)
    paste_button = tk.Button(
        source_labelframe, text=" Paste ",
        command=lambda: paste_input(source_textbox, source_charcode_label, config_option, source_charcount_label,
                                    filename_label), font="Arial 8 bold")
    copy_button = tk.Button(destination_labelframe,
                            text=" Copy ", command=lambda: copy_output(destination_textbox), font="Arial 8 bold")

    source_charcode_label = tk.Label(source_labelframe, text="None")
    destination_charcode_label = tk.Label(destination_labelframe, text="None")
    paste_button.grid(row=0, column=1, padx=5, pady=5)
    copy_button.grid(row=0, column=1, padx=5, pady=5)
    source_charcode_label.grid(row=0, column=2, padx=5, pady=5)
    destination_charcode_label.grid(row=0, column=2, padx=5, pady=5)
    source_charcount_label = tk.Label(
        source_labelframe, text=f"( {len(source_textbox.get('1.0', tk.END)) - 1} Chars )")
    source_charcount_label.place(relx=0.99, rely=0.5, anchor="e")

    action_labelframe = tk.LabelFrame(frame)
    action_labelframe.grid(
        row=2, column=0, sticky="news", padx=20, pady=(0, 20))
    openfile_button = tk.Button(
        action_labelframe, text=" Open File ",
        command=lambda: open_file(source_textbox, source_charcode_label, config_option, source_charcount_label,
                                  filename_label), font="Arial 10 bold")
    filename_label = tk.Label(action_labelframe, text="")
    convert_button = tk.Button(
        action_labelframe, text=" Convert ",
        command=lambda: convert(source_textbox, config_option, region_config_option, zhtw_option, punctuation_option,
                                destination_textbox, source_charcode_label, destination_charcode_label),
        font="Arial 12 bold")
    convert_button.grid(row=0, column=0, padx=390, pady=5)
    openfile_button.place(relx=0.01, rely=0.5, anchor="w")
    filename_label.place(relx=0.11, rely=0.5, anchor="w")
    exit_button = tk.Button(action_labelframe, text=" Exit ",
                            command=window.destroy, font="Arial 10 bold")
    exit_button.place(relx=0.99, rely=0.5, anchor="e")

    window.eval('tk::PlaceWindow . center')
    window.mainloop()


if __name__ == "__main__":
    main()
