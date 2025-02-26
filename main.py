import tkinter as tk
import os
import tkinter.font as tkfont
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename, askopenfilename


windows = tk.Tk()
width= windows.winfo_screenwidth()               
height= windows.winfo_screenheight()               
windows.geometry("%dx%d" % (width, height))
windows.title('My IDE')
file_path = ''

def set_file_path(path):
    global file_path
    file_path = path


def open_file():
    path = askopenfilename(filetypes=[('All Files', '*.*'), ('PHP Files', '*.php'),('Env Files', '*.env'),('Python Files', '*.py')])
    current_tab = tabControl.index("current")
    current_editor = editorlist[current_tab]
    with open(path, 'r') as file:
        code = file.read()
        current_editor.delete('1.0', tk.END)
        current_editor.insert('1.0', code)
        set_file_path(path)
        tabControl.tab(current_tab, text=os.path.basename(path))


def save_as():
    current_tab = tabControl.index("current")
    current_editor = editorlist[current_tab]
    if file_path == '':
        path = asksaveasfilename(filetypes=[('All Files', '*.*'), ('PHP Files', '*.php'),('Env Files', '*.env'),('Python Files', '*.py')])
    else:
        path = file_path
    with open(path, 'w') as file:
        code = current_editor.get('1.0', tk.END)
        file.write(code)
        set_file_path(path)

def create_tab():
    index_tabs = len(tabControl.tabs())
    next_tab = 'tab'+str(index_tabs)
    next_editor = 'editor'+str(index_tabs)
    next_tab = ttk.Frame(tabControl) 
    tabControl.add(next_tab, text ='new file') 
    next_editor = tk.Text(next_tab)
    font = tkfont.Font(font=next_editor["font"])
    tab_width = font.measure(" " * 4)
    next_editor.config(tabs=tab_width)
    next_editor.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
    editorlist.append(next_editor)

menu_bar = tk.Menu(windows)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label='Open', command=open_file, accelerator='Ctrl-O')
file_menu.add_command(label='Save', command=save_as, accelerator='Ctrl-S')
file_menu.add_command(label='Save As', command=save_as, accelerator='Ctrl-S')
file_menu.add_command(label='Exit', command=exit, accelerator='Ctrl-Q')
menu_bar.add_cascade(label='File', menu=file_menu)

tab_menu = tk.Menu(menu_bar, tearoff=0)
tab_menu.add_command(label='New', command=create_tab, accelerator='Ctrl-N')
tab_menu.add_command(label='Close current', command=create_tab, accelerator='Ctrl-C')
menu_bar.add_cascade(label='Tabs', menu=tab_menu)

windows.config(menu=menu_bar)
windows.bind('<Control-o>', lambda e:open_file())
windows.bind('<Control-s>', lambda e:save_as())
windows.bind('<Control-n>', lambda e:create_tab())
windows.bind('<Control-q>', exit)

windows.grid_rowconfigure(0, weight=3)
windows.grid_rowconfigure(1, weight=1)
windows.grid_columnconfigure(0, weight=1)

tabControl = ttk.Notebook(windows) 
tabControl.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S, padx=5, pady=5)

editorlist = []

tab0 = ttk.Frame(tabControl) 
tabControl.add(tab0, text ='new file') 
editor0 = tk.Text(tab0)
font = tkfont.Font(font=editor0["font"])
tab_width = font.measure(" " * 4)
editor0.config(tabs=tab_width)
editor0.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
editorlist.append(editor0)

code_output = tk.Text(height=5)
code_output.grid(row=1, column=0, sticky=tk.W + tk.E + tk.N + tk.S, padx=5, pady=5)

windows.mainloop()



