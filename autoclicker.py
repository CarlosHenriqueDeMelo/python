import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Listener, KeyCode

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Pro")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")
        
        self.clicking = False
        self.click_count = 0
        self.mouse = MouseController()
        self.delay = 0.1
        self.click_button = Button.left
        self.toggle_key = KeyCode.from_char('f6')
        self.listener = None
        
        self.setup_ui()
        self.start_keyboard_listener()
        
    def setup_ui(self):
        title = tk.Label(self.root, text="AutoClicker Pro", font=("Segoe UI", 18, "bold"), 
                        bg="#1e1e2e", fg="#89b4fa")
        title.pack(pady=15)
        
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(padx=25, pady=5, fill="both", expand=True)
        
        # Velocidade
        speed_frame = tk.LabelFrame(main_frame, text="Velocidade", bg="#313244", fg="#cdd6f4",
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
        
        # Tipo de Clique
        click_frame = tk.LabelFrame(main_frame, text="Tipo de Clique", bg="#313244", fg="#cdd6f4",
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
        
        # Modo
        mode_frame = tk.LabelFrame(main_frame, text="Modo", bg="#313244", fg="#cdd6f4",
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
        
        # Status
        status_frame = tk.Frame(main_frame, bg="#1e1e2e")
        status_frame.pack(fill="x", pady=10)
        
        self.status_label = tk.Label(status_frame, text="PARADO", font=("Segoe UI", 14, "bold"),
                                      bg="#1e1e2e", fg="#f38ba8")
        self.status_label.pack()
        
        self.count_label = tk.Label(status_frame, text="Cliques: 0", font=("Segoe UI", 12),
                                     bg="#1e1e2e", fg="#cdd6f4")
        self.count_label.pack(pady=5)
        
        # Botões
        btn_frame = tk.Frame(main_frame, bg="#1e1e2e")
        btn_frame.pack(fill="x", pady=10)
        
        self.toggle_btn = tk.Button(btn_frame, text="INICIAR (F6)", command=self.toggle_clicking,
                                     bg="#a6e3a1", fg="#1e1e2e", font=("Segoe UI", 12, "bold"),
                                     width=18, height=2, bd=0, cursor="hand2",
                                     activebackground="#81c8be", activeforeground="#1e1e2e")
        self.toggle_btn.pack(pady=5)
        
        tk.Button(btn_frame, text="Resetar Contador", command=self.reset_counter,
                   bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10),
                   width=18, bd=0, cursor="hand2", 
                   activebackground="#45475a", activeforeground="#cdd6f4").pack(pady=3)
        
        tk.Label(btn_frame, text="Atalho: F6 (Iniciar/Parar)", bg="#1e1e2e", 
                 fg="#6c7086", font=("Segoe UI", 9, "italic")).pack(pady=5)
        
        self.update_delay()
        
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
        self.status_label.config(text="CLICANDO", fg="#a6e3a1")
        self.toggle_btn.config(text="PARAR (F6)", bg="#f38ba8")
        
        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()
    
    def stop_clicking(self):
        self.clicking = False
        self.status_label.config(text="PARADO", fg="#f38ba8")
        self.toggle_btn.config(text="INICIAR (F6)", bg="#a6e3a1")
    
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
        if key == self.toggle_key:
            self.root.after(0, self.toggle_clicking)
    
    def start_keyboard_listener(self):
        self.listener = Listener(on_press=self.on_key_press)
        self.listener.start()
    
    def on_closing(self):
        self.clicking = False
        if self.listener:
            self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
