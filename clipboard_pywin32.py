import win32clipboard
import win32con
import contextlib

@contextlib.contextmanager
def clipboard():
    """Context manager for handling clipboard operations using pywin32."""
    try:
        win32clipboard.OpenClipboard()
        yield
    finally:
        win32clipboard.CloseClipboard()

def set_clipboard_text(text):
    """Sets the given text to the clipboard using pywin32."""
    with clipboard():
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        return True

def get_clipboard_text():
    """Gets text from the clipboard using pywin32."""
    with clipboard():
        try:
            data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            return data
        except Exception as e:  # Catch exceptions like EmptyClipboard or format errors
            print(f"Error getting clipboard data: {e}")
            return ""

# Example usage:
if __name__ == "__main__":
    text_to_copy = "Hello from pywin32 clipboard!"
    if set_clipboard_text(text_to_copy):
        print("Text copied to clipboard successfully.")

        retrieved_text = get_clipboard_text()
        if retrieved_text:
            print(f"Retrieved text from clipboard: {retrieved_text}")
        else:
            print("Failed to retrieve text from clipboard.")
    else:
        print("Failed to copy text to clipboard.")