import requests
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import difflib, os, time, requests
from pkg_resources import working_set

#------------------ OBJECTS -----------------

class DarkEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(
            master,
            bg="#1E1E1E",
            fg="#FFFFFF",
            insertbackground="#FFFFFF",
            highlightthickness=1,
            highlightbackground="#3C3C3C",
            highlightcolor="#3C3C3C",
            relief="flat",
            **kwargs
        )

# ------------------ LOGIC ------------------
def update_package(name):
    try:
        subprocess.check_call(["python", "-m", "pip", "install", "--upgrade", name])
        messagebox.showinfo("Updated: {name}")
    except Exception as e:
        messagebox.showerror("error:", str(e))

def is_package_installed(pkg_name):
    installed = {pkg.key.lower(): pkg.version for pkg in working_set}
    return installed.get(pkg_name.lower())

def fuzzy_search(keyword):
    cache_file = "pypi_index.txt"

    if not os.path.exists(cache_file) or time.time() - os.path.getmtime(cache_file) > 86400:
        try:
            res = requests.get("https://pypi.org/simple/", timeout=15)
            pkgs = [line.split('">')[1].split("</a>")[0]
                    for line in res.text.splitlines() if 'href' in line]
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write("\n".join(pkgs))
        except Exception as e:
            return [f"error: {e}"]

    with open(cache_file, "r", encoding="utf-8") as f:
        pkgs = f.read().splitlines()
        pkgs = [p for p in pkgs if keyword in p.lower()]

    matches = difflib.get_close_matches(keyword, pkgs, n=50, cutoff=0.3)
    return matches if matches else ["Not found..."]

def get_package_info(name):
    try:
        url = f"https://pypi.org/pypi/{name}/json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            info = data.get("info", {})
            return f"{info.get('name', name)} ({info.get('version', '?')})\n\n{info.get('summary', 'Unknown searching')}"
        else:
            return "Information not found."
    except Exception as e:
        return f"error: {e}"

def install_package(name):
    try:
        subprocess.check_call(["python", "-m", "pip", "install", name])
        messagebox.showinfo("Successful, Installed: {name}")
    except Exception as e:
        messagebox.showerror("error:", str(e))

def uninstall_package(name):
    try:
        subprocess.check_call(["python", "-m", "pip", "uninstall", "-y", name])
        messagebox.showinfo("Successful, Uninstalled: {name}")
    except Exception as e:
        messagebox.showerror("error:", str(e))

# ------------------ UI ------------------

def on_search():
    keyword = entry.get().strip()
    if not keyword:
        messagebox.showinfo("Notification", "Please enter a keyword to search.")
        return

    output_list.delete(0, tk.END)
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, f"🔍 Searching for '{keyword}'...\n")

    results = fuzzy_search(keyword.lower())
    for r in results:
        output_list.insert(tk.END, r)
    output_text.delete(1.0, tk.END)

def on_select(event):
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END,"Loading package info... please wait.")
    selected = output_list.get(output_list.curselection())
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, get_package_info(selected))
    if is_package_installed(selected):
        uninstall_btn.config(state="normal")
        uninstall_btn.name = selected
        install_btn.config(state="disabled")
        update_btn.config(state="normal")
        update_btn.name = selected
    else:
        install_btn.config(state="normal")
        install_btn.name = selected
        uninstall_btn.config(state="disabled")
        update_btn.config(state="disabled")


root = tk.Tk()
root.title("PyManager - Python Package Manager")
root.configure(bg="#282828")
root.geometry("900x600")

style = ttk.Style()
style.theme_use("clam")

style.configure(".", background="#282828", foreground="#FFFFFF", fieldbackground="#1E1E1E")

style.configure("TFrame", background="#282828")

style.configure("TLabel", background="#282828", foreground="#FFFFFF")

style.configure("TEntry", fieldbackground="#292929", foreground="#FFFFFF")

style.configure("TButton", background="#3C3C3C", foreground="#FFFFFF")
style.map("TButton",
          background=[("active", "#505050"), ("pressed", "#2E2E2E")])

style.configure("Vertical.TScrollbar", background="#3C3C3C", troughcolor="#282828")


top_frame = ttk.Frame(root, padding=10)
top_frame.pack(fill="x")
top_frame.configure(style="TFrame")
ttk.Label(top_frame, text="Keyword:", background="#282828", foreground="#FFFFFF").pack(side="left")
entry = DarkEntry(top_frame, width=50)
entry.pack(side="left", padx=5)
ttk.Button(top_frame, text="Search", command=on_search).pack(side="left", padx=5)

mid_frame = ttk.Frame(root)
mid_frame.pack(fill="both", expand=True, padx=10, pady=10)
mid_frame.configure(style="TFrame")

output_list = tk.Listbox(mid_frame, width=40)
output_list.pack(side="left", fill="y")
output_list.bind("<<ListboxSelect>>", on_select)
output_list.configure(bg="#1E1E1E", fg="#FFFFFF", selectbackground="#3C3C3C", selectforeground="#FFFFFF")

scrollbar = ttk.Scrollbar(mid_frame, orient="vertical", command=output_list.yview)
scrollbar.pack(side="left", fill="y")
output_list.config(yscrollcommand=scrollbar.set, bg="#1E1E1E", fg="#FFFFFF")
scrollbar.configure(style="Vertical.TScrollbar")

output_text = tk.Text(mid_frame, wrap="word")
output_text.pack(side="left", fill="both", expand=True, padx=10)
output_text.configure(bg="#1E1E1E", fg="#FFFFFF")

btn_frame = ttk.Frame(root, padding=10)
btn_frame.pack(fill="x")
btn_frame.configure(style="TFrame")

install_btn = ttk.Button(btn_frame, text="Install", state="disabled", command=lambda: install_package(install_btn.name))
install_btn.pack(side="left", padx=5)

uninstall_btn = ttk.Button(btn_frame, text="Uninstall", state="disabled", command=lambda: uninstall_package(uninstall_btn.name))
uninstall_btn.pack(side="left", padx=5)

update_btn = ttk.Button(btn_frame, text="Update", command=lambda: update_package(entry.get().strip()))
update_btn.pack(side='left', padx=5)

root.mainloop()
