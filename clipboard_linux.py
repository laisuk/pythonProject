import subprocess

def get_clipboard_text():
    try:
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'],
                                check=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,  # Important for proper string handling
                                encoding='utf-8')  # Explicitly set encoding
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting clipboard text (xclip): {e.stderr.decode('utf-8') if e.stderr else 'Unknown error'}") # Decode stderr
        return ""
    except FileNotFoundError:
        print("Error: xclip not found. Is it installed?")
        return ""


def set_clipboard_text(text):
    try:
        subprocess.run(['xclip', '-selection', 'clipboard'],
                       input=text,
                       check=True,
                       text=True,  # Important for proper string handling
                       encoding='utf-8')  # Explicitly set encoding
    except subprocess.CalledProcessError as e:
        print(f"Error setting clipboard text (xclip): {e.stderr.decode('utf-8') if e.stderr else 'Unknown error'}") # Decode stderr
    except FileNotFoundError:
        print("Error: xclip not found. Is it installed?")
        return ""

if __name__ == "__main__":
    text_to_copy = "Hello from cross-platform clipboard!  你好世界"  # Example with multibyte chars
    if set_clipboard_text(text_to_copy):
        print("Text copied to clipboard successfully.")

        retrieved_text = get_clipboard_text()
        if retrieved_text:
            print(f"Retrieved text from clipboard: {retrieved_text}")
        else:
            print("Failed to retrieve text from clipboard.")
    else:
        print("Failed to copy text to clipboard.")