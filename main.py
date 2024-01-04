import re
import tkinter as tk  # GUI
import jieba  # Segmentor module
import pyperclip as pc  # Clipboard module
from opencc import OpenCC  # use module: pip install -u opencc-python-reimplemented
from tkinter import filedialog as fd


def paste_input():
    text = pc.paste()
    source_textbox.delete("1.0", tk.END)
    source_textbox.insert("1.0", text)

    test_text = re.sub(r'[\WA-Za-z0-9_]', "", text)
    test_text = test_text if len(test_text) < 30 else test_text[0:30]

    match check_textcode(test_text):
        case 1:
            source_charcode_label.config(text="zh-Hant (繁体)")
            config_option.set(value="tw2sp")
        case 2:
            source_charcode_label.config(text="zh-Hans (简体)")
            config_option.set(value="s2twp")
        case _:
            source_charcode_label.config(text="Non-zh (其它)")

    source_charcount_label.config(text=f"( {len(text):,} Chars )")


def copy_output():
    pc.copy(destination_textbox.get("1.0", tk.END))


def openfile():
    filename = fd.askopenfilename(initialdir="./", title="Open File", filetypes=(
        ("Text Files", "*.txt"), ("Subtitle Files", "*.srt;*.vtt;*.ass;*.ttml2;*.xml"), ("All Files", "*.*")))
    with open(filename, "r", encoding="utf-8") as f:
        contents = f.read()

    source_textbox.delete("1.0", tk.END)
    source_textbox.insert("1.0", contents)

    test_text = re.sub(r'[\WA-Za-z0-9_]', "", contents)
    test_text = test_text if len(test_text) < 30 else test_text[0:30]

    match check_textcode(test_text):
        case 1:
            source_charcode_label.config(text="zh-Hant (繁体)")
            config_option.set(value="tw2sp")
        case 2:
            source_charcode_label.config(text="zh-Hans (简体)")
            config_option.set(value="s2twp")
        case _:
            source_charcode_label.config(text="Non-zh (其它)")

    source_charcount_label.config(text=f"( {len(contents):,} Chars )")


def convert():
    input_text = source_textbox.get("1.0", tk.END)
    if config_option.get() == "jieba":
        segment_list = jieba.cut(input_text)
        output_text = "/".join(segment_list)
    else:
        converter = OpenCC(config_option.get())
        output_text = converter.convert(input_text)
    destination_textbox.delete("1.0", tk.END)
    destination_textbox.insert("1.0", output_text)

    if config_option.get() != "jieba" and "Non-zh" not in source_charcode_label.cget("text"):
        destination_charcode_label.config(
            text="zh-Hant (繁体)" if config_option.get() == "s2twp" else "zh-Hans (简体)")
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


window = tk.Tk()
window.title("Hans <-> Hant Converter")

frame = tk.Frame(window)
frame.pack()

config_labelframe = tk.LabelFrame(frame, text="Configuration")
config_labelframe.grid(row=0, column=0, padx=20, pady=5, sticky="news")
config_option = tk.StringVar(value="tw2sp")

t2s_radiobutton = tk.Radiobutton(
    config_labelframe, text="zh-Hant (繁体) to zh-Hans (简体)", padx=20, pady=5, value="tw2sp", variable=config_option,
    font="Arial 12")
s2t_radiobutton = tk.Radiobutton(
    config_labelframe, text="zh-Hans (简体) to zh-hant (繁体)", padx=20, pady=5, value="s2twp", variable=config_option,
    font="Arial 12")
jieba_radiobutton = tk.Radiobutton(config_labelframe, text="Words Segmentor (拆词)", padx=20, pady=5, value="jieba",
                                   variable=config_option, font="Arial 12")

t2s_radiobutton.grid(row=0, column=0)
s2t_radiobutton.grid(row=0, column=1)
jieba_radiobutton.grid(row=0, column=2)

content_labelframe = tk.LabelFrame(frame, text="Contents")
content_labelframe.grid(row=1, column=0, padx=20, pady=5, sticky="news")

source_textbox = tk.Text(content_labelframe, width=50, height=25, font="10")
source_textbox.grid(row=0, column=0, padx=(10, 0), pady=5)
source_scrollbar = tk.Scrollbar(
    content_labelframe, command=source_textbox.yview)
source_scrollbar.grid(row=0, column=1, sticky="news")
source_textbox['yscrollcommand'] = source_scrollbar.set

destination_textbox = tk.Text(
    content_labelframe, width=50, height=25, font="10")
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
    source_labelframe, text=" Paste Input ", command=paste_input, font="Arial 8 bold")
copy_button = tk.Button(destination_labelframe,
                        text=" Copy Output ", command=copy_output, font="Arial 8 bold")

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
action_labelframe.grid(row=2, column=0, sticky="news", padx=20, pady=(0, 20))
openfile_button = tk.Button(
    action_labelframe, text=" Open File ", command=openfile, font="Arial 10 bold")
convert_button = tk.Button(
    action_labelframe, text=" Convert ", command=convert, font="Arial 12 bold")
convert_button.grid(row=0, column=0, padx=390, pady=5)
openfile_button.place(relx=0.01, rely=0.5, anchor="w")
exit_button = tk.Button(action_labelframe, text=" Exit ",
                        command=window.destroy, font="Arial 10 bold")
exit_button.place(relx=0.99, rely=0.5, anchor="e")

window.eval('tk::PlaceWindow . center')
window.mainloop()
