import customtkinter as ctk
import yt_dlp
import threading
import os
import re
import sys
import winsound
from tkinter import filedialog
from PIL import Image

# Safe import for pywin32
try:
    import win32com.client
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

# --- Path Configuration Function ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

LOGO_PATH = resource_path("logo.ico")
BG_PATH = resource_path("sol.png")
CONFIG_FILE = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__), "solman_config.txt")

EULA_TEXT = """SOLMAN PRO (ሶልማን ፕሮ)
Copyright © 2026 Solomon Alemayehu. All rights reserved.

By installing this software, you agree to the following terms:
1. Ownership: This software is the property of Solomon Alemayehu.
2. Restriction: Unauthorized distribution is prohibited.
3. Usage: The user is responsible for the content they download.
4. Privacy: This app does not collect personal data."""

class InstallationSetup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("SOLMAN PRO - Setup")
        self.geometry("500x680")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.parent.quit)
        self.attributes("-topmost", True)
        
        try:
            if os.path.exists(LOGO_PATH): self.iconbitmap(LOGO_PATH)
        except: pass

        self.current_step = 1
        self.license_var = ctk.StringVar(value="reject")
        self.shortcut_var = ctk.BooleanVar(value=True)
        
        self.configure(fg_color="#E2DADA")
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)
        self.show_step()

    def show_step(self):
        for widget in self.main_container.winfo_children(): widget.destroy()
        if self.current_step == 1: self.welcome_step()
        elif self.current_step == 2: self.license_step()
        elif self.current_step == 3: self.ready_step()

    def welcome_step(self):
        ctk.CTkLabel(self.main_container, text="Welcome!", font=("Arial", 28, "bold"), text_color="#3B8ED0").pack(pady=(50, 20))
        ctk.CTkLabel(self.main_container, text="This wizard will guide you through the\ninstallation of SOLMAN PRO.", font=("Arial", 16)).pack(pady=20)
        self.nav_buttons(show_back=False, next_text="Next")

    def license_step(self):
        ctk.CTkLabel(self.main_container, text="License Agreement", font=("Arial", 20, "bold")).pack(pady=10)
        license_box = ctk.CTkTextbox(self.main_container, width=420, height=280, fg_color="#E0D8D8", font=("Arial", 13))
        license_box.insert("0.0", EULA_TEXT)
        license_box.configure(state="disabled")
        license_box.pack(pady=10)
        self.rb_accept = ctk.CTkRadioButton(self.main_container, text="I accept the agreement", variable=self.license_var, value="accept", command=self.toggle_next)
        self.rb_accept.pack(pady=5, anchor="w", padx=40)
        self.rb_reject = ctk.CTkRadioButton(self.main_container, text="I do not accept the agreement", variable=self.license_var, value="reject", command=self.toggle_next)
        self.rb_reject.pack(pady=5, anchor="w", padx=40)
        self.nav_buttons(next_text="Next")
        self.toggle_next()

    def ready_step(self):
        ctk.CTkLabel(self.main_container, text="Ready to Install", font=("Arial", 24, "bold"), text_color="#2fa572").pack(pady=(50, 20))
        self.cb_shortcut = ctk.CTkCheckBox(self.main_container, text="Create Desktop Shortcut", variable=self.shortcut_var)
        self.cb_shortcut.pack(pady=20)
        self.nav_buttons(next_text="Install")

    def toggle_next(self):
        state = "normal" if self.license_var.get() == "accept" else "disabled"
        self.btn_next.configure(state=state)

    def nav_buttons(self, show_back=True, next_text="Next"):
        btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=20)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="#c42b2b", width=110, command=self.parent.quit).pack(side="left", padx=10)
        self.btn_next = ctk.CTkButton(btn_frame, text=next_text, fg_color="#3B8ED0", width=110, command=self.next_action)
        self.btn_next.pack(side="right", padx=10)
        if show_back: ctk.CTkButton(btn_frame, text="Back", fg_color="#2E2D2D", width=110, command=self.prev_step).pack(side="right", padx=10)

    def next_action(self):
        if self.current_step < 3: 
            self.current_step += 1
            self.show_step()
        else: 
            self.finish_install()

    def prev_step(self): 
        self.current_step -= 1
        self.show_step()

    def finish_install(self):
        if self.shortcut_var.get():
            self.create_shortcut() # Call directly
        try: winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
        except: pass
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: f.write("INSTALLED=YES")
        self.destroy()
        self.parent.deiconify()

    def create_shortcut(self):
        if not HAS_PYWIN32: return
        try:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            path = os.path.join(desktop, "SOLMAN PRO.lnk")
            target = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            if os.path.exists(LOGO_PATH): 
                shortcut.IconLocation = target if getattr(sys, 'frozen', False) else LOGO_PATH
            shortcut.save()
        except Exception as e:
            print(f"Shortcut Error: {e}")

class SolmanPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        
        try:
            if os.path.exists(LOGO_PATH): self.iconbitmap(LOGO_PATH)
        except: pass

        self.title("SOLMAN PRO | Downloader")
        self.geometry("550x800")
        self.resizable(False, False)

        if os.path.exists(BG_PATH):
            bg_image = Image.open(BG_PATH)
            self.bg_photo = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(550, 800))
            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        if os.path.exists(CONFIG_FILE): self.deiconify()
        else: self.show_installer()

        self.save_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        self.setup_ui()

    def show_installer(self): 
        InstallationSetup(self)

    def setup_ui(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, pady=(30, 10), sticky="ew")
        self.header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.header, text="SOLMAN PRO", font=("Impact", 50), text_color="#3B8ED0").grid(row=0, column=0)

        self.url_card = ctk.CTkFrame(self, fg_color=("#1E1E1E"), corner_radius=15, border_width=1, border_color="#333333")
        self.url_card.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.url_card.grid_columnconfigure((0, 1, 2), weight=1)

        self.url_entry = ctk.CTkEntry(self.url_card, placeholder_text="Paste YouTube URL here...", height=50, border_width=0, fg_color="#2B2B2B")
        self.url_entry.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="ew")

        ctk.CTkButton(self.url_card, text="📋 Paste", fg_color="#333333", command=self.paste_url).grid(row=1, column=0, padx=(20, 5), pady=(0, 20), sticky="ew")
        ctk.CTkButton(self.url_card, text="🖱️ Select", fg_color="#333333", command=self.select_all).grid(row=1, column=1, padx=5, pady=(0, 20), sticky="ew")
        ctk.CTkButton(self.url_card, text="🧹 Clear", fg_color="#442222", hover_color="#662222", command=self.clear_url).grid(row=1, column=2, padx=(5, 20), pady=(0, 20), sticky="ew")

        self.set_card = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15, border_width=1, border_color="#333333")
        self.set_card.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        self.set_card.grid_columnconfigure((0, 1), weight=1)
        
        self.mode = ctk.CTkSegmentedButton(self.set_card, values=["Video", "Audio"], command=self.update_q)
        self.mode.set("Video")
        self.mode.grid(row=0, column=0, columnspan=2, padx=20, pady=15, sticky="ew")
        
        self.q_menu = ctk.CTkOptionMenu(self.set_card, values=["1080p", "720p", "480p"], fg_color="#2B2B2B")
        self.q_menu.set("720p")
        self.q_menu.grid(row=1, column=0, padx=(20, 10), pady=15, sticky="ew")
        
        ctk.CTkButton(self.set_card, text="📁 Save Folder", border_width=1, fg_color="transparent", command=self.sel_folder).grid(row=1, column=1, padx=(10, 20), pady=15, sticky="ew")

        self.pr_card = ctk.CTkFrame(self, fg_color="#161616", corner_radius=15, border_width=1, border_color="#333333")
        self.pr_card.grid(row=3, column=0, padx=30, pady=10, sticky="ew")
        self.pr_card.grid_columnconfigure(0, weight=1)
        
        self.pct_lbl = ctk.CTkLabel(self.pr_card, text="Ready", font=("Arial", 14, "bold"))
        self.pct_lbl.grid(row=0, column=0, pady=(10, 5))
        self.p_bar = ctk.CTkProgressBar(self.pr_card, height=12, progress_color="#3B8ED0")
        self.p_bar.set(0)
        self.p_bar.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.sp_lbl = ctk.CTkLabel(self.pr_card, text="Speed: 0 MiB/s", text_color="grey")
        self.sp_lbl.grid(row=2, column=0, pady=(0, 10))

        self.dl_btn = ctk.CTkButton(self, text="🚀 START DOWNLOAD", height=60, corner_radius=30, font=("Arial", 18, "bold"), fg_color="#2fa572", command=self.start)
        self.dl_btn.grid(row=4, column=0, padx=30, pady=20, sticky="ew")
        self.grid_rowconfigure(5, weight=1)

    def paste_url(self):
        try:
            self.url_entry.delete(0, 'end')
            self.url_entry.insert(0, self.clipboard_get())
        except: pass

    def select_all(self):
        self.url_entry.focus()
        self.url_entry.select_range(0, 'end')

    def clear_url(self):
        self.url_entry.delete(0, 'end')

    def sel_folder(self):
        p = filedialog.askdirectory()
        if p: self.save_path = p

    def update_q(self, m):
        if m == "Video": self.q_menu.configure(values=["1080p", "720p", "480p"]); self.q_menu.set("720p")
        else: self.q_menu.configure(values=["320kbps", "192kbps", "128kbps"]); self.q_menu.set("320kbps")

    def hook(self, d):
        if d['status'] == 'downloading':
            try:
                p_str = d.get('_percent_str', '0')
                p = float(re.sub(r'[^0-9.]', '', p_str)) / 100
                self.p_bar.set(p)
                self.pct_lbl.configure(text=f"Downloading: {int(p*100)}%")
                self.sp_lbl.configure(text=f"Speed: {d.get('_speed_str', 'N/A')}")
            except: pass
        elif d['status'] == 'finished':
            self.p_bar.set(1.0)
            self.pct_lbl.configure(text="Finalizing...", text_color="yellow")

    def start(self):
        u = self.url_entry.get().strip()
        if not u: return
        self.dl_btn.configure(state="disabled", text="PROCESSING...")
        threading.Thread(target=self.run, args=(u,), daemon=True).start()

    def run(self, u):
        m, q = self.mode.get(), self.q_menu.get()
        opts = {'outtmpl': f'{self.save_path}/%(title)s.%(ext)s', 'progress_hooks': [self.hook], 'quiet': True}
        if m == "Audio":
            opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': q.replace("kbps","")}]})
        else:
            opts['format'] = f'bestvideo[height<={q.replace("p","")}]+bestaudio/best'
        try:
            with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([u])
            self.pct_lbl.configure(text="✅ COMPLETE!", text_color="#2fa572")
        except: self.pct_lbl.configure(text="❌ ERROR", text_color="red")
        finally: self.dl_btn.configure(state="normal", text="🚀 START DOWNLOAD")

if __name__ == "__main__":
    app = SolmanPro()
    app.mainloop()





































    