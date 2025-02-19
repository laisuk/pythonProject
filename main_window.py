import os
import tkinter as tk
from tkinter.filedialog import askopenfilename
from opencc_jieba_rs import OpenCC
from zho_helper import check_text_code, convert_punctuation
from clipboard_common import set_clipboard_text


class ZhoTkApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide the root window
        # === Main Window === #
        self.root.title("zh-Hans <=> zh-Hant Converter")
        self.root.geometry("1000x720")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.frame = tk.Frame(self.root)
        # frame.pack()
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure((0, 1), weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.frame.grid(column=0, row=0, sticky="news")

        self.config_labelframe = tk.LabelFrame(self.frame, text="Configuration")
        self.config_labelframe.grid(row=0, column=0, padx=20, pady=5, sticky="ew")
        self.config_labelframe.columnconfigure((0, 1, 2), weight=1)
        self.config_labelframe.rowconfigure((0, 1, 2), weight=1)
        self.config_option = tk.StringVar(value="t2s")
        self.region_config_option = tk.StringVar(value="std")
        self.zhtw_option = tk.IntVar(value=0)
        self.punctuation_option = tk.IntVar(value=1)

        self.t2s_radiobutton = tk.Radiobutton(
            self.config_labelframe, text="zh-Hant (繁体) to zh-Hans (简体)", padx=20, pady=5, value="t2s",
            variable=self.config_option,
            font="Arial 12")
        self.s2t_radiobutton = tk.Radiobutton(
            self.config_labelframe, text="zh-Hans (简体) to zh-hant (繁体)", padx=20, pady=5, value="s2t",
            variable=self.config_option,
            font="Arial 12")
        self.jieba_radiobutton = tk.Radiobutton(self.config_labelframe, text="Words Segmentor (分词)",
                                                padx=20, pady=5, value="jieba", variable=self.config_option,
                                                font="Arial 12")

        self.std_radiobutton = tk.Radiobutton(self.config_labelframe, text="Standard (标准简繁)",
                                              variable=self.region_config_option, value="std",
                                              command=self.std_hk_select, font="Arial 10")
        self.zhtw_radiobutton = tk.Radiobutton(self.config_labelframe, text="Mainland/Taiwan (中台简繁)",
                                               variable=self.region_config_option, value="zhtw",
                                               command=self.zhtw_select, font="Arial 10")
        self.hk_radiobutton = tk.Radiobutton(self.config_labelframe, text="Hong Kong (中港简繁)",
                                             variable=self.region_config_option, value="hk",
                                             command=self.std_hk_select, font="Arial 10")

        self.zhtw_checkbutton = tk.Checkbutton(
            self.config_labelframe, text="ZH/TW Idioms (中台惯用语)", variable=self.zhtw_option, font="Arial 10",
            command=self.zhtw_click)
        self.punctuation_checkbutton = tk.Checkbutton(
            self.config_labelframe, text="Punctuation (标点符号)", variable=self.punctuation_option, font="Arial 10")

        self.t2s_radiobutton.grid(row=0, column=0)
        self.s2t_radiobutton.grid(row=0, column=1)
        self.jieba_radiobutton.grid(row=0, column=2)
        self.std_radiobutton.grid(row=1, column=0)
        self.zhtw_radiobutton.grid(row=1, column=1)
        self.hk_radiobutton.grid(row=1, column=2)
        self.zhtw_checkbutton.grid(row=2, column=1)
        self.punctuation_checkbutton.grid(row=2, column=2)

        self.content_labelframe = tk.LabelFrame(self.frame, text="Contents")
        self.content_labelframe.columnconfigure((0, 2), weight=1)
        self.content_labelframe.columnconfigure((1, 3), minsize=20)
        self.content_labelframe.rowconfigure((0, 1), weight=1)
        self.content_labelframe.grid(row=1, column=0, padx=20, pady=5, sticky="news")

        self.source_textbox = tk.Text(self.content_labelframe, font=("Consolas", 11))
        self.source_textbox.grid(row=0, column=0, padx=(10, 0), pady=5, sticky="news")
        self.source_scrollbar = tk.Scrollbar(
            self.content_labelframe, command=self.source_textbox.yview)
        self.source_scrollbar.grid(row=0, column=1, sticky="news", padx=(0, 5))
        self.source_textbox['yscrollcommand'] = self.source_scrollbar.set

        self.destination_textbox = tk.Text(
            self.content_labelframe, font=("Consolas", 11))
        self.destination_textbox.grid(row=0, column=2, padx=(5, 0), pady=5, sticky="news")
        self.destination_scrollbar = tk.Scrollbar(
            self.content_labelframe, command=self.destination_textbox.yview)
        self.destination_scrollbar.grid(row=0, column=3, sticky="news", padx=(0, 10))
        self.destination_textbox['yscrollcommand'] = self.destination_scrollbar.set

        self.source_labelframe = tk.LabelFrame(self.content_labelframe)
        self.destination_labelframe = tk.LabelFrame(self.content_labelframe)
        self.source_labelframe.grid(row=1, column=0, sticky="news",
                                    padx=(10, 5), pady=5, columnspan=2)
        self.destination_labelframe.grid(
            row=1, column=2, sticky="news", padx=(5, 10), pady=5, columnspan=2)
        self.source_label = tk.Label(self.source_labelframe, text="Source")
        self.destination_label = tk.Label(self.destination_labelframe, text="Destination")
        self.source_label.grid(row=0, column=0, padx=5, pady=5)
        self.destination_label.grid(row=0, column=0, padx=5, pady=5)
        self.paste_button = tk.Button(
            self.source_labelframe, text=" Paste ",
            command=self.paste_input, font="Arial 8 bold")
        self.copy_button = tk.Button(self.destination_labelframe,
                                     text=" Copy ", command=self.copy_output, font="Arial 8 bold")

        self.source_char_code_label = tk.Label(self.source_labelframe, text="None")
        self.destination_char_code_label = tk.Label(self.destination_labelframe, text="None")
        self.paste_button.grid(row=0, column=1, padx=5, pady=5)
        self.copy_button.grid(row=0, column=1, padx=5, pady=5)
        self.source_char_code_label.grid(row=0, column=2, padx=5, pady=5)
        self.destination_char_code_label.grid(row=0, column=2, padx=5, pady=5)
        self.source_char_count_label = tk.Label(
            self.source_labelframe, text=f"( {len(self.source_textbox.get('1.0', tk.END)) - 1} Chars )")
        self.source_char_count_label.place(relx=0.99, rely=0.5, anchor="e")

        self.action_labelframe = tk.LabelFrame(self.frame, height=20)
        self.action_labelframe.columnconfigure((0, 1, 2), weight=1, uniform="a")
        self.action_labelframe.rowconfigure(0, weight=1)
        self.action_labelframe.grid(
            row=2, column=0, sticky="news", padx=20, pady=(0, 10))
        self.openfile_button = tk.Button(
            self.action_labelframe, text=" Open File ",
            command=self.open_file, font="Arial 10 bold")
        self.filename_label = tk.Label(self.action_labelframe, text="")
        self.convert_button = tk.Button(
            self.action_labelframe, text=" Convert ",
            command=self.convert,
            font="Arial 12 bold")

        self.openfile_button.grid(row=0, column=0, sticky="w", padx=10)
        self.filename_label.grid(row=0, column=0, sticky="w", padx=100)
        self.convert_button.grid(row=0, column=1, sticky="")
        self.exit_button = tk.Button(self.action_labelframe, text=" Exit ",
                                     command=self.root.destroy, font="Arial 10 bold")
        self.exit_button.grid(row=0, column=2, sticky="e", padx=10)

    def clipboard_tk_get(self) -> str:
        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError:
            clipboard_text = ''
        self.root.update()
        return clipboard_text

    def clipboard_tk_set(self, text: str) -> None:
        if isinstance(text, str):
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        self.root.update()

    # Use this tkinter clipboard module in case pyperclip not working in WSL
    def clipboard_tk_get_set(self, text_to_paste=None):
        # import tkinter # For Python 2, replace with "import Tkinter as tkinter".
        if isinstance(text_to_paste, str):  # Set clipboard text.
            self.root.clipboard_clear()
            self.root.clipboard_append(text_to_paste)
        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError:
            clipboard_text = ''
        # Stops a few errors
        # (clipboard text unchanged, command line program unresponsive, window not destroyed).
        self.root.update()
        return clipboard_text

    def paste_input(self):
        # text = pc.paste()
        text = self.clipboard_tk_get()
        # text = get_clipboard_text()
        self.update_textbox(text)

        self.source_char_count_label.config(text=f"( {len(text):,} Chars )")
        self.filename_label.config(text="")

    def update_textbox(self, text):
        self.source_textbox.delete("1.0", tk.END)
        self.source_textbox.insert("1.0", text)

        self.update_source_info(check_text_code(text))

    def update_source_info(self, text_code):
        if text_code == 1:
            self.source_char_code_label.config(text="zh-Hant (繁体)")
            self.config_option.set(value="t2s")
        elif text_code == 2:
            self.source_char_code_label.config(text="zh-Hans (简体)")
            self.config_option.set(value="s2t")
        else:
            self.source_char_code_label.config(text="Non-zh (其它)")

    def copy_output(self):
        # pc.copy(destination_textbox.get("1.0", 'end-2c'))
        # self.clipboard_tk_set(self.destination_textbox.get("1.0", 'end-2c'))
        set_clipboard_text(self.destination_textbox.get("1.0", 'end-2c'))

    def open_file(self):
        filename = askopenfilename(initialdir="./", title="Open File", filetypes=(
            ("Text Files", "*.txt"), ("All Files", "*.*")))

        if not filename:
            return

        with open(filename, "r", encoding="utf-8") as f:
            contents = f.read()

        self.update_textbox(contents)

        self.source_char_count_label.config(text=f"( {len(contents):,} Chars )")
        self.filename_label.config(text=os.path.basename(filename))

    def convert(self):
        output_text = ""
        input_text = self.source_textbox.get("1.0", tk.END)

        if input_text == "\n":
            return

        if self.config_option.get() == "jieba":
            segment_list = OpenCC().jieba_cut(input_text)
            # segment_list = 'Feature disabled'
            output_text = "/".join(segment_list)
        else:
            region_config = self.region_config_option.get()
            if region_config == "std":
                converter = OpenCC(self.config_option.get())
                output_text = converter.convert(input_text)
                # print(converter.config)
            elif region_config == "zhtw":
                converter = OpenCC(self.config_option.get().replace("t", "tw") +
                                   "p" if self.zhtw_option.get() else self.config_option.get().replace("t", "tw"))
                output_text = converter.convert(input_text)
                # print(converter.config)
            elif region_config == "hk":
                converter = OpenCC(self.config_option.get().replace(
                    "t", "hk"))
                output_text = converter.convert(input_text)
                # print(converter.config)

        if self.punctuation_option.get() and "jieba" not in self.config_option.get():
            output_text = convert_punctuation(output_text, self.config_option.get())

        self.destination_textbox.delete("1.0", tk.END)
        self.destination_textbox.insert("1.0", output_text)

        if self.config_option.get() != "jieba" and "Non-zh" not in self.source_char_code_label.cget("text"):
            self.destination_char_code_label.config(
                text="zh-Hant (繁体)" if self.config_option.get() == "s2t" else "zh-Hans (简体)")
        else:
            self.destination_char_code_label.config(
                text=self.source_char_code_label.cget("text"))

    def std_hk_select(self):
        self.zhtw_option.set(0)

    def zhtw_select(self):
        self.zhtw_option.set(1)

    def zhtw_click(self):
        self.region_config_option.set("zhtw")

    def run(self):
        self.root.deiconify()  # Show the window
        self.root.eval('tk::PlaceWindow . center')
        self.root.mainloop()


# Running the app
if __name__ == "__main__":
    ttk = tk.Tk()
    app = ZhoTkApp(ttk)
    app.run()
