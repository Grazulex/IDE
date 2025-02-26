import tkinter as tk
import os
import subprocess
import tkinter.font as tkfont
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename, askopenfilename

windows = tk.Tk()
width = windows.winfo_screenwidth()
height = windows.winfo_screenheight()
windows.geometry(f"{width}x{height}")
windows.title("My IDE")
file_paths = {}  # Stocke le chemin de chaque tab individuellement

def set_file_path(index, path):
    file_paths[index] = path

def open_file():
    path = askopenfilename(filetypes=[("All Files", "*.*"), ("Python Files", "*.py"), ("PHP Files", "*.php"), ("Env Files", "*.env")])
    if not path:
        return
    current_tab = tabControl.index("current")
    current_editor = editorlist[current_tab]
    with open(path, "r") as file:
        code = file.read()
        current_editor.delete("1.0", tk.END)
        current_editor.insert("1.0", code)
        set_file_path(current_tab, path)
        tabControl.tab(current_tab, text=os.path.basename(path))

def save_as():
    current_tab = tabControl.index("current")
    current_editor = editorlist[current_tab]
    path = file_paths.get(current_tab, '')
    if not path:
        path = asksaveasfilename(filetypes=[("All Files", "*.*"), ("Python Files", "*.py"), ("PHP Files", "*.php"), ("Env Files", "*.env")])
        if not path:
            return
    with open(path, "w") as file:
        code = current_editor.get("1.0", tk.END)
        file.write(code)
        set_file_path(current_tab, path)
        
def create_tab():
    index_tabs = len(tabControl.tabs())
    new_tab = ttk.Frame(tabControl)
    tabControl.add(new_tab, text="new file")
    new_editor = tk.Text(new_tab)
    font = tkfont.Font(font=new_editor["font"])
    tab_width = font.measure(" " * 4)
    new_editor.config(tabs=tab_width)
    new_editor.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    editorlist.append(new_editor)
    file_paths[index_tabs] = ""  # Ajoute un chemin vide pour ce nouvel onglet

def close_current_tab():
    current_tab = tabControl.index("current")
    tabControl.forget(current_tab)
    del editorlist[current_tab]
    del file_paths[current_tab]

def run_code():
    current_tab = tabControl.index("current")
    current_editor = editorlist[current_tab]
    code = current_editor.get("1.0", tk.END)
    with open("temp_script.py", "w") as temp_file:
        temp_file.write(code)
    result = subprocess.run(["python", "temp_script.py"], capture_output=True, text=True)
    code_output.delete("1.0", tk.END)
    code_output.insert("1.0", result.stdout + result.stderr)

menu_bar = tk.Menu(windows)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open", command=open_file, accelerator="Ctrl-O")
file_menu.add_command(label="Save", command=save_as, accelerator="Ctrl-S")
file_menu.add_command(label="Save As", command=save_as)
file_menu.add_command(label="Exit", command=windows.quit, accelerator="Ctrl-Q")
menu_bar.add_cascade(label="File", menu=file_menu)

tab_menu = tk.Menu(menu_bar, tearoff=0)
tab_menu.add_command(label="New", command=create_tab, accelerator="Ctrl-N")
tab_menu.add_command(label="Close current", command=close_current_tab, accelerator="Ctrl-W")
menu_bar.add_cascade(label="Tabs", menu=tab_menu)

run_menu = tk.Menu(menu_bar, tearoff=0)
run_menu.add_command(label="Run Python Script", command=run_code, accelerator="F5")
menu_bar.add_cascade(label="Run", menu=run_menu)

windows.config(menu=menu_bar)
windows.bind("<Control-o>", lambda event: open_file())
windows.bind("<Control-s>", lambda event: save_as())
windows.bind("<Control-n>", lambda event: create_tab())
windows.bind("<Control-w>", lambda event: close_current_tab())
windows.bind("<F5>", lambda event: run_code())

tabControl = ttk.Notebook(windows)
tabControl.pack(expand=1, fill="both")
editorlist = []

def create_first_tab():
    tab = ttk.Frame(tabControl)
    tabControl.add(tab, text="new file")
    editor = tk.Text(tab)
    font = tkfont.Font(font=editor["font"])
    tab_width = font.measure(" " * 4)
    editor.config(tabs=tab_width)
    editor.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    editorlist.append(editor)
    file_paths[0] = ""

create_first_tab()

code_output = tk.Text(windows, height=5, bg="#1e1e1e", fg="white")
code_output.pack(fill=tk.BOTH, padx=5, pady=5)

windows.mainloop()
