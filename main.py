import tkinter as tk
import os
import subprocess
import tkinter.font as tkfont
import re
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename, askopenfilename

windows = tk.Tk()
width = windows.winfo_screenwidth()
height = windows.winfo_screenheight()
windows.geometry(f"{width}x{height}")
windows.title("My IDE")
file_paths = {}  # Stocke le chemin de chaque tab individuellement

def run_git_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

def show_git_status():
    output = run_git_command("git status")
    git_output.delete("1.0", tk.END)
    git_output.insert("1.0", output)

def commit_changes():
    message = commit_message.get()
    if message.strip():
        run_git_command("git add .")
        output = run_git_command(f'git commit -m "{message}"')
        git_output.delete("1.0", tk.END)
        git_output.insert("1.0", output)
    else:
        git_output.delete("1.0", tk.END)
        git_output.insert("1.0", "Commit message cannot be empty!")

def push_changes():
    output = run_git_command("git push")
    git_output.delete("1.0", tk.END)
    git_output.insert("1.0", output)

def pull_changes():
    output = run_git_command("git pull")
    git_output.delete("1.0", tk.END)
    git_output.insert("1.0", output)

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
    apply_syntax_highlighting(current_editor)

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

def apply_syntax_highlighting(editor, line_numbers):
    editor.tag_remove("keyword", "1.0", tk.END)
    editor.tag_remove("string", "1.0", tk.END)
    editor.tag_remove("comment", "1.0", tk.END)
    editor.tag_remove("constant", "1.0", tk.END)
    editor.tag_remove("operator", "1.0", tk.END)
    editor.tag_remove("annotation", "1.0", tk.END)
    
    keywords = ["<?php", "echo", "function", "class", "if", "else", "while", "foreach", "switch", "case", "default", "break", "return", "public", "private", "protected", "static", "extends", "implements"]
    constants = ["true", "false", "null", "int", "string", "float", "bool"]
    operators = ["=>", "==", "===", "!=", "<=", ">=", "+", "-", "*", "/", "%"]
    annotations = ["@param", "@return", "@var"]
    
    pattern_keywords = r'\b(' + '|'.join(keywords) + r')\b'
    pattern_constants = r'\b(' + '|'.join(constants) + r')\b'
    pattern_operators = r'(' + '|'.join(re.escape(op) for op in operators) + r')'
    pattern_annotations = r'(' + '|'.join(annotations) + r')'
    pattern_string = r'(".*?"|\'.*?\')'
    pattern_comment = r'(//.*?$|/\*.*?\*/)' 
    
    text = editor.get("1.0", tk.END)
    
    def index_from_pos(pos):
        line_num = text.count("\n", 0, pos) + 1
        char_count = pos - (text.rfind("\n", 0, pos) + 1) if "\n" in text[:pos] else pos
        return f"{line_num}.{char_count}"
    
    for pattern, tag in [(pattern_keywords, "keyword"), (pattern_constants, "constant"), (pattern_operators, "operator"), (pattern_annotations, "annotation"), (pattern_string, "string"), (pattern_comment, "comment")]:
        for match in re.finditer(pattern, text, re.MULTILINE):
            editor.tag_add(tag, index_from_pos(match.start()), index_from_pos(match.end()))
    
    editor.tag_config("keyword", foreground="blue")
    editor.tag_config("constant", foreground="purple")
    editor.tag_config("operator", foreground="red")
    editor.tag_config("annotation", foreground="orange")
    editor.tag_config("string", foreground="green")
    editor.tag_config("comment", foreground="gray")

    update_line_numbers(line_numbers, editor)

def handle_keypress(event, editor):
    if event.keysym == "Return":
        line_start = editor.index("insert linestart")
        current_line = editor.get(line_start, f"{line_start} lineend").strip()
        indentation = len(editor.get(line_start, f"{line_start} lineend")) - len(current_line)
        
        if "{" in current_line:
            new_indent = indentation + 4
            editor.insert("insert", "\n" + " " * new_indent)
            return "break"
        elif "}" in current_line:
            new_indent = max(0, indentation - 4)
            editor.insert("insert", "\n" + " " * new_indent)
            return "break"
        elif any(current_line.startswith(kw) for kw in ["public", "private", "protected", "final", "static"]):
            new_indent = indentation
            editor.insert("insert", "\n" + " " * new_indent)
            return "break"
        else:
            editor.insert("insert", "\n" + " " * indentation)
            return "break"
    
    elif event.keysym == "Tab":
        editor.insert("insert", "    ")
        return "break"
    
    elif event.keysym == "braceleft":
        editor.insert("insert", "{\n" + " " * 4)
        return "break"
    
    elif event.keysym == "braceright":
        line_start = editor.index("insert linestart")
        current_line = editor.get(line_start, f"{line_start} lineend").strip()
        indentation = len(editor.get(line_start, f"{line_start} lineend")) - len(current_line)
        new_indent = max(0, indentation - 4)
        editor.insert("insert", "\n" + " " * new_indent + "}\n" + " " * new_indent)
        return "break"

def update_line_numbers(line_numbers, editor):
    line_numbers.config(state="normal")
    line_numbers.delete("1.0", tk.END)
    line_count = editor.index("end-1c").split(".")[0]
    line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, int(line_count) + 1)))
    line_numbers.config(state="disabled")
        
def create_tab():
    index_tabs = len(tabControl.tabs())

    new_tab = ttk.Frame(tabControl)
    tabControl.add(new_tab, text="new file")

    frame = tk.Frame(new_tab)
    frame.pack(expand=True, fill=tk.BOTH)

    line_numbers = tk.Text(frame, width=4, padx=5, takefocus=0, border=0, background="#f0f0f0", state="disabled")
    line_numbers.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

    new_editor = tk.Text(frame)
    new_editor.pack(expand=True, fill=tk.BOTH, padx=5, pady=5, side=tk.RIGHT)

    new_editor.bind("<KeyRelease>", lambda event: apply_syntax_highlighting(new_editor, line_numbers))
    new_editor.bind("<KeyPress>", lambda event: handle_keypress(event, new_editor))
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

    frame = tk.Frame(tab)
    frame.pack(expand=True, fill=tk.BOTH)

    line_numbers = tk.Text(frame, width=4, padx=5, takefocus=0, border=0, background="#f0f0f0", state="disabled")
    line_numbers.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

    editor = tk.Text(frame)
    editor.pack(expand=True, fill=tk.BOTH, padx=5, pady=5, side=tk.RIGHT)

    editor.bind("<KeyRelease>", lambda event: apply_syntax_highlighting(editor, line_numbers))
    editor.bind("<KeyPress>", lambda event: handle_keypress(event, editor))

    editorlist.append(editor)
    file_paths[0] = ""

create_first_tab()

frame_bottom = tk.Frame(windows)
frame_bottom.pack(fill=tk.X, padx=5, pady=5)

git_frame = tk.Frame(frame_bottom)
git_frame.pack(side=tk.RIGHT, padx=5)

tk.Label(git_frame, text="Commit Message:").pack()
commit_message = tk.Entry(git_frame, width=40)
commit_message.pack()

tk.Button(git_frame, text="Git Status", command=show_git_status).pack(side=tk.LEFT, padx=2)
tk.Button(git_frame, text="Commit", command=commit_changes).pack(side=tk.LEFT, padx=2)
tk.Button(git_frame, text="Pull", command=pull_changes).pack(side=tk.LEFT, padx=2)
tk.Button(git_frame, text="Push", command=push_changes).pack(side=tk.LEFT, padx=2)

git_output = tk.Text(frame_bottom, height=5, bg="#1e1e1e", fg="white")
git_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side=tk.LEFT)

code_output = tk.Text(windows, height=5, bg="#1e1e1e", fg="white")
code_output.pack(fill=tk.BOTH, padx=5, pady=5)

windows.mainloop()
