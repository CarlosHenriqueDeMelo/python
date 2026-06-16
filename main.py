import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, KeyCode, Key

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Pro v2")
        self.root.geometry("420x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.clicking = False
        self.click_count = 0
        self.mouse = MouseController()
        self.delay = 0.1
        self.click_button = Button.left

        # Tecla de atalho - agora personalizável!
        self.toggle_key = Key.f6
        self.toggle_key_name = "F6"
        self.listener = None
        self.capturing_key = False  # Flag para capturar nova tecla

        self.setup_ui()
        self.start_keyboard_listener()

    def setup_ui(self):
        title = tk.Label(self.root, text="AutoClicker Pro v2", font=("Segoe UI", 18, "bold"), 
                        bg="#1e1e2e", fg="#89b4fa")
        title.pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(padx=25, pady=5, fill="both", expand=True)

        # === TECLA DE ATALHO (NOVO!) ===
        shortcut_frame = tk.LabelFrame(main_frame, text="⌨️ Tecla de Atalho", bg="#313244", 
                                       fg="#cdd6f4", font=("Segoe UI", 11, "bold"), padx=15, pady=10)
        shortcut_frame.pack(fill="x", pady=5)

        self.key_label = tk.Label(shortcut_frame, text="F6", font=("Segoe UI", 16, "bold"),
                                   bg="#45475a", fg="#f9e2af", width=8, height=1,
                                   relief="ridge", bd=2)
        self.key_label.pack(pady=5)

        self.capture_btn = tk.Button(shortcut_frame, text="🎯 Capturar Nova Tecla", 
                                      command=self.start_key_capture,
                                      bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                                      width=20, bd=0, cursor="hand2",
                                      activebackground="#b4befe", activeforeground="#1e1e2e")
        self.capture_btn.pack(pady=5)

        self.capture_status = tk.Label(shortcut_frame, text="", bg="#313244", 
                                        fg="#a6e3a1", font=("Segoe UI", 9))
        self.capture_status.pack()

        # === VELOCIDADE ===
        speed_frame = tk.LabelFrame(main_frame, text="⚡ Velocidade", bg="#313244", fg="#cdd6f4",
                                     font=("Segoe UI", 11, "bold"), padx=15, pady=10)
        speed_frame.pack(fill="x", pady=5)

        tk.Label(speed_frame, text="Cliques/segundo:", bg="#313244", fg="#cdd6f4",
                 font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")

        self.cps_var = tk.DoubleVar(value=10.0)
        self.cps_spin = tk.Spinbox(speed_frame, from_=1, to=100, textvariable=self.cps_var,
                                     width=8, format="%.1f")
        self.cps_spin.grid(row=0, column=1, padx=10)
        self.cps_spin.bind("<KeyRelease>", self.update_delay)
        self.cps_spin.bind("<ButtonRelease>", self.update_delay)

        self.delay_label = tk.Label(speed_frame, text="Delay: 100ms", bg="#313244", 
                                     fg="#a6e3a1", font=("Segoe UI", 9))
        self.delay_label.grid(row=0, column=2, padx=10)

        # === TIPO DE CLIQUE ===
        click_frame = tk.LabelFrame(main_frame, text="🖱️ Tipo de Clique", bg="#313244", fg="#cdd6f4",
                                     font=("Segoe UI", 11, "bold"), padx=15, pady=10)
        click_frame.pack(fill="x", pady=5)

        self.click_type_var = tk.StringVar(value="left")
        tk.Radiobutton(click_frame, text="Esquerdo", variable=self.click_type_var, 
                       value="left", bg="#313244", fg="#cdd6f4", selectcolor="#1e1e2e",
                       activebackground="#313244", activeforeground="#cdd6f4",
                       font=("Segoe UI", 10), command=self.update_click_button).grid(row=0, column=0, padx=5)
        tk.Radiobutton(click_frame, text="Direito", variable=self.click_type_var, 
                       value="right", bg="#313244", fg="#cdd6f4", selectcolor="#1e1e2e",
                       activebackground="#313244", activeforeground="#cdd6f4",
                       font=("Segoe UI", 10), command=self.update_click_button).grid(row=0, column=1, padx=5)
        tk.Radiobutton(click_frame, text="Meio", variable=self.click_type_var, 
                       value="middle", bg="#313244", fg="#cdd6f4", selectcolor="#1e1e2e",
                       activebackground="#313244", activeforeground="#cdd6f4",
                       font=("Segoe UI", 10), command=self.update_click_button).grid(row=0, column=2, padx=5)

        # === MODO ===
        mode_frame = tk.LabelFrame(main_frame, text="🔁 Modo", bg="#313244", fg="#cdd6f4",
                                    font=("Segoe UI", 11, "bold"), padx=15, pady=10)
        mode_frame.pack(fill="x", pady=5)

        self.mode_var = tk.StringVar(value="single")
        tk.Radiobutton(mode_frame, text="Simples", variable=self.mode_var, 
                       value="single", bg="#313244", fg="#cdd6f4", selectcolor="#1e1e2e",
                       activebackground="#313244", activeforeground="#cdd6f4",
                       font=("Segoe UI", 10)).grid(row=0, column=0, padx=5)
        tk.Radiobutton(mode_frame, text="Duplo", variable=self.mode_var, 
                       value="double", bg="#313244", fg="#cdd6f4", selectcolor="#1e1e2e",
                       activebackground="#313244", activeforeground="#cdd6f4",
                       font=("Segoe UI", 10)).grid(row=0, column=1, padx=5)

        # === STATUS ===
        status_frame = tk.Frame(main_frame, bg="#1e1e2e")
        status_frame.pack(fill="x", pady=8)

        self.status_label = tk.Label(status_frame, text="⏹️ PARADO", font=("Segoe UI", 14, "bold"),
                                      bg="#1e1e2e", fg="#f38ba8")
        self.status_label.pack()

        self.count_label = tk.Label(status_frame, text="Cliques: 0", font=("Segoe UI", 12),
                                     bg="#1e1e2e", fg="#cdd6f4")
        self.count_label.pack(pady=3)

        # === BOTÕES ===
        btn_frame = tk.Frame(main_frame, bg="#1e1e2e")
        btn_frame.pack(fill="x", pady=5)

        self.toggle_btn = tk.Button(btn_frame, text="▶️ INICIAR", command=self.toggle_clicking,
                                     bg="#a6e3a1", fg="#1e1e2e", font=("Segoe UI", 12, "bold"),
                                     width=18, height=2, bd=0, cursor="hand2",
                                     activebackground="#81c8be", activeforeground="#1e1e2e")
        self.toggle_btn.pack(pady=5)

        tk.Button(btn_frame, text="🔄 Resetar", command=self.reset_counter,
                   bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10),
                   width=18, bd=0, cursor="hand2", 
                   activebackground="#45475a", activeforeground="#cdd6f4").pack(pady=3)

        self.update_delay()

    # === CAPTURAR NOVA TECLA ===
    def start_key_capture(self):
        if self.capturing_key:
            return

        self.capturing_key = True
        self.capture_status.config(text="Pressione qualquer tecla...", fg="#f9e2af")
        self.capture_btn.config(text="⌛ Aguardando...", bg="#f9e2af")
        self.key_label.config(bg="#6c7086", text="?")

        # Parar listener atual
        if self.listener:
            self.listener.stop()

        # Iniciar listener de captura (temporário)
        self.capture_listener = Listener(on_press=self.on_capture_key)
        self.capture_listener.start()

    def on_capture_key(self, key):
        if not self.capturing_key:
            return

        # Ignorar teclas modificadoras sozinhas
        if key in (Key.shift, Key.shift_r, Key.ctrl, Key.ctrl_r, 
                   Key.alt, Key.alt_r, Key.cmd, Key.cmd_r):
            return

        self.toggle_key = key
        self.toggle_key_name = self.get_key_name(key)

        # Atualizar interface
        self.root.after(0, self.update_key_display)

        # Parar listener de captura
        self.capture_listener.stop()
        self.capturing_key = False

        # Reiniciar listener normal
        self.root.after(100, self.start_keyboard_listener)

    def update_key_display(self):
        self.key_label.config(text=self.toggle_key_name, bg="#45475a")
        self.capture_btn.config(text="🎯 Capturar Nova Tecla", bg="#89b4fa")
        self.capture_status.config(text=f"Tecla '{self.toggle_key_name}' configurada!", fg="#a6e3a1")
        self.toggle_btn.config(text=f"▶️ INICIAR ({self.toggle_key_name})")

    def get_key_name(self, key):
        """Converte a tecla para nome legível"""
        if hasattr(key, 'char') and key.char:
            return key.char.upper()
        else:
            # Teclas especiais
            key_names = {
                Key.f1: "F1", Key.f2: "F2", Key.f3: "F3", Key.f4: "F4",
                Key.f5: "F5", Key.f6: "F6", Key.f7: "F7", Key.f8: "F8",
                Key.f9: "F9", Key.f10: "F10", Key.f11: "F11", Key.f12: "F12",
                Key.space: "ESPAÇO", Key.enter: "ENTER", Key.esc: "ESC",
                Key.tab: "TAB", Key.backspace: "BACKSPACE", Key.delete: "DELETE",
                Key.insert: "INSERT", Key.home: "HOME", Key.end: "END",
                Key.page_up: "PAGE UP", Key.page_down: "PAGE DOWN",
                Key.up: "↑", Key.down: "↓", Key.left: "←", Key.right: "→",
                Key.caps_lock: "CAPS LOCK", Key.num_lock: "NUM LOCK",
                Key.scroll_lock: "SCROLL LOCK", Key.print_screen: "PRINT SCREEN",
                Key.pause: "PAUSE", Key.menu: "MENU",
            }
            return key_names.get(key, str(key).replace("Key.", "").upper())

    def update_delay(self, event=None):
        try:
            cps = float(self.cps_var.get())
            if cps > 0:
                self.delay = 1.0 / cps
                self.delay_label.config(text=f"Delay: {self.delay*1000:.0f}ms")
        except:
            pass

    def update_click_button(self):
        btn = self.click_type_var.get()
        if btn == "left":
            self.click_button = Button.left
        elif btn == "right":
            self.click_button = Button.right
        else:
            self.click_button = Button.middle

    def toggle_clicking(self):
        if self.clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def start_clicking(self):
        self.clicking = True
        self.click_count = 0
        self.status_label.config(text="▶️ CLICANDO", fg="#a6e3a1")
        self.toggle_btn.config(text=f"⏹️ PARAR ({self.toggle_key_name})", bg="#f38ba8")

        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False
        self.status_label.config(text="⏹️ PARADO", fg="#f38ba8")
        self.toggle_btn.config(text=f"▶️ INICIAR ({self.toggle_key_name})", bg="#a6e3a1")

    def click_loop(self):
        while self.clicking:
            if self.mode_var.get() == "double":
                self.mouse.click(self.click_button, 2)
                self.click_count += 2
            else:
                self.mouse.click(self.click_button, 1)
                self.click_count += 1

            self.root.after(0, self.update_count_label)
            time.sleep(self.delay)

    def update_count_label(self):
        self.count_label.config(text=f"Cliques: {self.click_count}")

    def reset_counter(self):
        self.click_count = 0
        self.count_label.config(text="Cliques: 0")

    def on_key_press(self, key):
        # Ignorar se estiver capturando tecla
        if self.capturing_key:
            return

        if key == self.toggle_key:
            self.root.after(0, self.toggle_clicking)

    def start_keyboard_listener(self):
        if self.listener:
            self.listener.stop()
        self.listener = Listener(on_press=self.on_key_press)
        self.listener.start()

    def on_closing(self):
        self.clicking = False
        if self.listener:
            self.listener.stop()
        if hasattr(self, 'capture_listener') and self.capture_listener:
            self.capture_listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()