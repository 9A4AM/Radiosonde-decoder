import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import queue
import configparser
import os
import re
import sys
import ctypes


SETTINGS_FILE = "settings.ini"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DECODER_DIR = os.path.join(BASE_DIR, "rs", "decoders")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RTL_FM_PATH = os.path.join(BASE_DIR, "rs", "rtl_fm.exe")

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and py2exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class RS1729App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("9A4AM Radiosonde Decoder")
        self.geometry("1050x550")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.iconbitmap(resource_path("rs92.ico"))

        self.set_dark_theme()

        self.config = configparser.ConfigParser()
        self.load_settings()

        self.decoder_type = tk.StringVar(value=self.config.get("Decoder", "type", fallback="RS41"))
        self.freq_var = tk.StringVar(value=self.config.get("RTL_FM", "frequency", fallback="404"))
        self.gain_var = tk.StringVar(value=self.config.get("RTL_FM", "gain", fallback="49.6"))
        self.ppm_var = tk.StringVar(value=self.config.get("RTL_FM", "ppm", fallback="0"))

        self.process_rtl = None
        self.process_decoder = None
        self.output_queue = queue.Queue()
        self.current_payload_id = None

        self.last_data_keys = [
            "Payload_ID", "Longitude", "Latitude", "Altitude",
            "Direction", "Vertical_speed", "Horizontal_speed"
        ]

        self.last_data = {key: tk.StringVar(value="") for key in self.last_data_keys}





        self.favorite_freqs = []
        self.selected_fav_freq = tk.StringVar()

        self.ensure_favlist_exists()
        self.load_favorite_frequencies()
        self.create_widgets()
        self.create_last_data_window()

        self.after(100, self.process_output_queue)





    def ensure_favlist_exists(self):
        if not os.path.exists("favlist.txt"):
            default_freqs = ["405.3", "404", "401", "403", "403.7"]
            with open("favlist.txt", "w") as f:
                f.write("\n".join(default_freqs))

    def load_favorite_frequencies(self):
        try:
            with open("favlist.txt", "r") as f:
                self.favorite_freqs = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.favorite_freqs = []



    def set_dark_theme(self):
        import tkinter.font as tkFont
        style = ttk.Style(self)
        style.theme_use('clam')

        dark_bg = "#2e2e2e"
        highlight_bg = "#444444"
        text_bg = "#1e1e1e"
        dark_fg = "#FFD700"
        text_fg = "white"

        self.configure(bg=dark_bg)

        font_large = tkFont.Font(family="Segoe UI", size=12)

        style.configure(".", background=dark_bg, foreground=dark_fg, fieldbackground=dark_bg, font=font_large)
        style.configure("TLabel", background=dark_bg, foreground=dark_fg, font=font_large)
        style.configure("TFrame", background=dark_bg)
        style.configure("TLabelFrame", background=dark_bg, foreground=dark_fg, font=font_large)
        style.configure("TRadiobutton", background=dark_bg, foreground=dark_fg, font=font_large)
        style.configure("TButton", background=highlight_bg, foreground=dark_fg, font=font_large)
        style.map("TButton",
                  background=[('active', '#555555')],
                  foreground=[('active', '#ffffff')])


        style.configure('Gold.TCombobox',
                        fieldbackground=dark_bg,
                        background=dark_bg,
                        foreground=dark_fg,
                        font=font_large)


        style.map('Gold.TCombobox',
                  fieldbackground=[('readonly', dark_bg), ('!focus', dark_bg)],
                  foreground=[('readonly', dark_fg), ('!focus', dark_fg)])

        # Boje i font za Text widget
        self.text_bg = text_bg
        self.text_fg = text_fg
        self.text_font = font_large



    def create_widgets(self):
        frame_decoder = ttk.LabelFrame(self, text="Typ radiosonde - decoder selection")
        frame_decoder.pack(padx=10, pady=5, fill="x")
        ttk.Radiobutton(frame_decoder, text="RS41", variable=self.decoder_type, value="RS41").pack(side="left", padx=10, pady=5)
        ttk.Radiobutton(frame_decoder, text="M10", variable=self.decoder_type, value="M10").pack(side="left", padx=10, pady=5)
        ttk.Radiobutton(frame_decoder, text="M20", variable=self.decoder_type, value="M20").pack(side="left", padx=10, pady=5)
        ttk.Radiobutton(frame_decoder, text="DFM", variable=self.decoder_type, value="DFM").pack(side="left", padx=10, pady=5)


        frame_rtl = ttk.LabelFrame(self, text="RTL_FM Settings")
        frame_rtl.pack(padx=10, pady=5, fill="x")

        frame_fav = ttk.LabelFrame(self, text="Favorite Frequencies")
        frame_fav.pack(padx=10, pady=5, fill="x")

        for freq in self.favorite_freqs:
            ttk.Radiobutton(
                frame_fav, text=f"{freq} MHz", variable=self.selected_fav_freq, value=freq,
                command=lambda: self.freq_var.set(f"{self.selected_fav_freq.get()}")
            ).pack(side="left", padx=5, pady=2)


        # ttk.Label(frame_rtl, text="Frequency (Hz):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(frame_rtl, text="Frequency (MHz):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_rtl, textvariable=self.freq_var, width=20).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(frame_rtl, text="Gain:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        # ttk.Entry(frame_rtl, textvariable=self.gain_var, width=20).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        gain_options = [
            "49.6", "48", "44.5", "43.9", "43.4", "42.1", "40.2", "38.6",
            "37.2", "36.4", "33.8", "32.8", "29.7", "28", "25.4", "22.9",
            "20.7", "19.7", "16.6", "15.7", "14.4", "12.5", "8.7", "7.7",
            "3.7", "2.7", "1.4", "0.9", "0"
        ]

        self.gain_combobox = ttk.Combobox(frame_rtl, values=gain_options, textvariable=self.gain_var,
                                          width=18, state="readonly", style='Gold.TCombobox')
        self.gain_combobox.grid(row=1, column=1, sticky="w", padx=5, pady=2)


        if self.gain_var.get() in gain_options:
            self.gain_combobox.current(gain_options.index(self.gain_var.get()))
        else:
            self.gain_combobox.current(0)

        ttk.Label(frame_rtl, text="PPM:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(frame_rtl, textvariable=self.ppm_var, width=20).grid(row=2, column=1, sticky="w", padx=5, pady=2)

        frame_buttons = ttk.Frame(self)
        frame_buttons.pack(padx=10, pady=10, fill="x")
        self.status_label = tk.Label(self, text="Status: Decoder Inactive", font=("Helvetica", 12), fg="red", bg="#2e2e2e")
        self.status_label.pack(padx=10, pady=(0, 10), anchor="w")
        ttk.Button(frame_buttons, text="START decoder", command=self.start_decoder).pack(side="left", padx=10)
        ttk.Button(frame_buttons, text="STOP decoder", command=self.stop_decoder).pack(side="left", padx=10)


        label_9a4am = tk.Label(frame_buttons, text="Radiosonde decoder v2.1 by 9A4AM@2025", font=("Helvetica", 20), fg="white", bg="#2e2e2e")
        label_9a4am.pack(side="left", padx=10)



        frame_output = ttk.Frame(self)
        frame_output.pack(padx=10, pady=5, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame_output)
        scrollbar.pack(side="right", fill="y")
        self.output_text = tk.Text(frame_output, wrap="none", yscrollcommand=scrollbar.set,
                                   state="disabled",
                                   bg=self.text_bg, fg=self.text_fg,
                                   insertbackground=self.text_fg)
        self.output_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.output_text.yview)

    def create_last_data_window(self):
        self.update_idletasks()


        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()


        new_x = main_x + main_width + 10
        new_y = main_y

        self.last_window = tk.Toplevel(self)
        self.last_window.title("Last received data")
        self.last_window.iconbitmap(resource_path("rs92.ico"))

        # self.last_window.overrideredirect(True)
        self.last_window.protocol("WM_DELETE_WINDOW", lambda: None)
        self.last_window.attributes("-topmost", True)
        self.last_window.geometry(f"400x250+{new_x}+{new_y}")
        self.last_window.configure(bg="#2e2e2e")
        self.last_window.attributes("-topmost", True)

        for i, key in enumerate(self.last_data_keys):
            label_text = key.replace("_", " ")
            ttk.Label(self.last_window, text=label_text + ":").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            val_label = ttk.Label(self.last_window, textvariable=self.last_data[key])
            val_label.grid(row=i, column=1, sticky="w", padx=5, pady=2)


    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            self.config.read(SETTINGS_FILE)
        else:
            self.config["Decoder"] = {"type": "RS41"}
            self.config["RTL_FM"] = {"frequency": "405.3", "gain": "33.8", "ppm": "0"}
            with open(SETTINGS_FILE, "w") as f:
                self.config.write(f)

    def save_settings(self):
        self.config["Decoder"] = {"type": self.decoder_type.get()}
        self.config["RTL_FM"] = {
            "frequency": self.freq_var.get(),
            "gain": self.gain_var.get(),
            "ppm": self.ppm_var.get()
        }
        with open(SETTINGS_FILE, "w") as f:
            self.config.write(f)

    def start_decoder(self):
        self.save_settings()
        self.focus_set()
        if self.process_rtl or self.process_decoder:
            messagebox.showinfo("Info", "Decoder is already started!")
            return
        try:
            freq = self.freq_var.get().strip() + "M"
            float(freq.replace("M", "").replace("k", ""))
            gain = float(self.gain_var.get())
            ppm = int(self.ppm_var.get())
        except ValueError:
            messagebox.showerror("Error", "Input correct nummeric data for frequency, gain and ppm.")
            return

        rtl_cmd = [
            RTL_FM_PATH, "-f", str(freq), "-g", str(gain),
            "-p", str(ppm), "-M", "raw", "-s", "48000", "-"
        ]

        decoder_map = {
            "RS41": "rs41mod.exe",
            "M10": "m10mod.exe",
            "M20": "mXXmod.exe",
            "DFM": "dfm09mod.exe"
        }
        decoder_name = decoder_map.get(self.decoder_type.get())
        decoder_exe = os.path.join(DECODER_DIR, decoder_name)
        if not os.path.isfile(decoder_exe):
            messagebox.showerror("Error", f"Decoder not found: {decoder_exe}")
            return

        # rs_cmd = [decoder_exe, "-vv", "--IQ", "0.0", "--lp", "-", "48000", "16y"]
        rs_cmd = [decoder_exe, "-v", "--IQ", "0.0", "--lp", "-", "48000", "16y"]
        try:
            self.process_rtl = subprocess.Popen(rtl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.process_decoder = subprocess.Popen(rs_cmd, stdin=self.process_rtl.stdout,
                                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.process_rtl.stdout.close()
            threading.Thread(target=self.read_output_thread, daemon=True).start()
            threading.Thread(target=self.read_error_thread, daemon=True).start()
            self.log_message("Decoder started .\n")
            self.status_label.config(text="Status: Decoder activ", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Procces not started:\n{e}")
            self.process_rtl = None
            self.process_decoder = None


    def stop_decoder(self):
        if self.process_decoder:
            self.process_decoder.terminate()
            self.process_decoder = None
        if self.process_rtl:
            self.process_rtl.terminate()
            self.process_rtl = None
        self.log_message("Decoder stopped.\n")
        self.status_label.config(text="Status: Decoder inactiv", fg="red")

    def read_output_thread(self):
        try:
            for line in iter(self.process_decoder.stdout.readline, b''):
                if not line:
                    break
                text = line.decode(errors="replace").strip()
                self.output_queue.put(text)
        except Exception as e:
            self.output_queue.put(f"[Error reading output]: {e}")

    def read_error_thread(self):
        try:
            for line in iter(self.process_decoder.stderr.readline, b''):
                if not line:
                    break
                text = line.decode(errors="replace").strip()
                self.output_queue.put("[ERR] " + text)
        except Exception as e:
            self.output_queue.put(f"[Error stderr]: {e}")

    def process_output_queue(self):
        while not self.output_queue.empty():
            text = self.output_queue.get().strip()


            if "[ERR] IF: 48000" in text:
                from tkinter import messagebox
                messagebox.showerror("SDR Error", "Error! SDR not exist or not installed ZADIG driver!")
                self.log_message("[SDR ERROR] " + text + "\n")


                if hasattr(self, 'decoder_process'):
                    try:
                        self.decoder_process.terminate()
                        self.decoder_process = None
                    except Exception as e:
                        print(f"[ERROR] Decoder interrupted: {e}")
                return

            self.log_message(text + "\n")
            self.check_and_log_payload(text)
            self.update_last_data(text)

        self.after(100, self.process_output_queue)

    def log_message(self, message):
        self.output_text.config(state="normal")
        self.output_text.insert("end", message)
        self.output_text.see("end")
        self.output_text.config(state="disabled")

    def check_and_log_payload(self, text):
        match = re.search(r'\(([A-Z][0-9A-Z]+)\)', text)
        if match:
            payload_id = match.group(1)
            if self.current_payload_id != payload_id:
                self.current_payload_id = payload_id
                # self.output_queue.put(f"[INFO] New sonde ID: {self.current_payload_id}")

        if self.current_payload_id:
            try:

                # log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
                if getattr(sys, 'frozen', False):

                    application_path = os.path.dirname(sys.executable)
                else:

                    application_path = os.path.dirname(os.path.abspath(__file__))

                log_dir = os.path.join(application_path, "log")
                os.makedirs(log_dir, exist_ok=True)

                filename = f"{self.current_payload_id}.log"
                filepath = os.path.join(log_dir, filename)

                with open(filepath, "a", encoding="utf-8") as f:
                    f.write(text + "\n")
            except Exception as e:
                self.output_queue.put(f"[Logging error]: {e}")

    def update_last_data(self, text):
        try:

            match = re.search(r'\(([A-Z0-9]+)\)', text)
            if match and "Payload_ID" in self.last_data:
                self.last_data["Payload_ID"].set(match.group(1))
            elif "Payload_ID" in self.last_data:
                self.last_data["Payload_ID"].set("N/A")


            fields = {
                "Latitude": r'lat:\s*([-+]?\d*\.\d+)',
                "Longitude": r'lon:\s*([-+]?\d*\.\d+)',
                "Altitude": r'alt:\s*([-+]?\d*\.\d+)',
                "Horizontal_speed": r'vH:\s*([-+]?\d*\.\d+)',
                "Direction": r'D:\s*([-+]?\d*\.\d+)',
                "Vertical_speed": r'vV:\s*([-+]?\d*\.\d+)'
            }


            for key, pattern in fields.items():
                match = re.search(pattern, text)
                if match:
                    if key in self.last_data:
                        value = match.group(1)
                        if key == "Horizontal_speed":

                            try:
                                kmh = float(value) * 3.6
                                self.last_data[key].set(f"{kmh:.1f} km/h")
                            except ValueError:
                                self.last_data[key].set("N/A")
                        else:
                            self.last_data[key].set(value)
                else:
                    if key in self.last_data:
                        self.last_data[key].set("N/A")


        except Exception as e:
            print(f"[Error] in update_last_data: {e}")
            # self.log_data(f"[Not valid packet] {text}")




    def cleanup_processes(self):
        os.system("taskkill /f /im rtl_fm.exe >nul 2>&1")
        os.system("taskkill /f /im rs41mod.exe >nul 2>&1")
        os.system("taskkill /f /im mXXmod.exe >nul 2>&1")


    def on_closing(self):
        self.cleanup_processes()
        self.destroy()



if __name__ == "__main__":
    app = RS1729App()
    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("Decoder closed.")
        app.stop_decoder()

