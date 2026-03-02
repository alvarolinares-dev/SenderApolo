import os
import subprocess
import time

def copy_file_to_clipboard_win(path):
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"No existe: {abs_path}")
    
    ps_command = f'Add-Type -AssemblyName System.Windows.Forms; ' \
                 f'$file = Get-Item "{abs_path}"; ' \
                 f'[System.Windows.Forms.Clipboard]::SetFileDropList([System.Collections.Specialized.StringCollection]@($file.FullName))'
    
    try:
        print(f"Executing: {ps_command}")
        subprocess.run(["powershell", "-Command", ps_command], check=True)
        print("Success!")
    except Exception as e:
        print(f"Error Windows Clipboard: {e}")
        raise e

if __name__ == "__main__":
    # Create a dummy file to test
    test_file = "test_document.txt"
    with open(test_file, "w") as f:
        f.write("This is a test document for clipboard verification.")
    
    try:
        copy_file_to_clipboard_win(test_file)
        print("Verification script finished. Please try to 'Paste' (Ctrl+V) in a folder or WhatsApp to verify.")
    finally:
        # We leave the file for the user to see if they want, or we can delete it.
        # os.remove(test_file)
        pass
