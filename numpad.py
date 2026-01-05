import tkinter as tk
from tkinter import ttk
import keyboard  # pip install keyboard
import ctypes

# --- Windows API 常量 ---
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000

class FloatingNumpad:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Excel Numpad")
        # 默认尺寸
        self.root.geometry("350x350+1000+500")
        self.root.configure(bg="#1f2937")
        self.root.overrideredirect(True)
        
        self.is_pinned = True
        self.alpha_value = 0.95
        
        # 颜色配置
        self.colors = {
            "bg": "#1f2937",
            "header": "#111827",
            "btn_num": "#374151",
            "btn_act": "#4b5563",
            "btn_enter": "#2563eb",
            "text": "#ffffff",
            "text_muted": "#9ca3af"
        }
        
        self.setup_ui()
        
        # 初始化置顶状态 (使用原生方法更稳定)
        self.root.attributes('-topmost', self.is_pinned)
        self.root.attributes('-alpha', self.alpha_value)

        # self.debug_label = tk.Label(self.root, text="就绪", fg="green")
        # self.debug_label.pack()
        # 延迟应用无焦点样式
        self.root.after(10, self.apply_window_styles)
        
    def setup_ui(self):
        # 1. 标题栏 (拖动区域)
        self.header = tk.Frame(self.root, bg=self.colors["header"], height=40)
        self.header.pack(fill="x", side="top")
        self.header.bind("<Button-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)
        
        # 标题
        tk.Label(self.header, text="小键盘 Pro", bg=self.colors["header"], fg=self.colors["text_muted"], 
                font=("微软雅黑", 10, "bold")).pack(side="left", padx=10)
        
        # 顶部按钮区
        btn_config = {"bg": self.colors["header"], "bd": 0, "activebackground": self.colors["btn_act"], "cursor": "hand2"}
        
        # 关闭
        tk.Button(self.header, text="✕", command=self.root.destroy, fg="#ef4444", width=4, font=("Arial", 10), **btn_config).pack(side="right")
        
        # 设置 (显隐透明度条)
        tk.Button(self.header, text="⚙", command=self.toggle_settings, fg=self.colors["text"], font=("Arial", 12), **btn_config).pack(side="right", padx=2)
        
        # 置顶切换
        self.pin_btn = tk.Button(self.header, text="📌", command=self.toggle_pin, fg="#3b82f6", font=("Arial", 10), **btn_config)
        self.pin_btn.pack(side="right", padx=2)

        # 2. 设置面板 (默认隐藏)
        self.settings_panel = tk.Frame(self.root, bg=self.colors["header"], pady=5)
        tk.Label(self.settings_panel, text="透明度:", bg=self.colors["header"], fg="white", font=("微软雅黑", 9)).pack(side="left", padx=10)
        self.scale = tk.Scale(self.settings_panel, from_=0.3, to=1.0, resolution=0.05, orient="horizontal", 
                            bg=self.colors["header"], fg="white", highlightthickness=0, bd=0, 
                            command=self.set_alpha, showvalue=0)
        self.scale.set(self.alpha_value)
        self.scale.pack(side="left", fill="x", expand=True, padx=10)

        # 3. 按键区域 (自动填充剩余空间)
        self.grid_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=6, pady=6)
        self.grid_frame.pack(fill="both", expand=True)
        self.create_keys()

        # 4. 调整大小的手柄 (右下角)
        self.grip = tk.Label(self.root, text="◢", bg=self.colors["bg"], fg="#6b7280", cursor="sizing", font=("Arial", 12))
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        self.grip.bind("<Button-1>", self.start_resize)
        self.grip.bind("<B1-Motion>", self.do_resize)

    def create_keys(self):
        # 布局定义
        # (Label, Row, Col)
        keys = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('⌫', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('C', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('Enter', 2, 3),
            ('0', 3, 0), ('.', 3, 2)  # 修正：小数点移到第3列 (index 2)
        ]
        
        # 网格权重，让按钮随窗口缩放
        for i in range(4): self.grid_frame.grid_columnconfigure(i, weight=1)
        for i in range(4): self.grid_frame.grid_rowconfigure(i, weight=1)

        for key, r, c in keys:
            rowspan = 1
            colspan = 1
            bg = self.colors["btn_num"]
            fg = self.colors["text"]
            cmd = lambda k=key: self.on_click(k)
            
            if key == "0": colspan = 2 # 0 占两列
            if key == "Enter": 
                rowspan = 2
                bg = self.colors["btn_enter"]
            if key == "⌫": bg = self.colors["btn_act"]
            if key == "C": 
                bg = "#7f1d1d" # 深红
                cmd = self.clear_input

            btn = tk.Button(self.grid_frame, text=key, bg=bg, fg=fg,
                          font=("Segoe UI", 16, "bold"), bd=0,
                          activebackground=fg, activeforeground=bg,
                          command=cmd)
            btn.grid(row=r, column=c, rowspan=rowspan, columnspan=colspan, 
                    sticky="nsew", padx=2, pady=2)

    def apply_window_styles(self):
        # 获取窗口句柄并添加 "无焦点" 属性
        # 注意：置顶属性由 attributes('-topmost') 管理，这里只管 NOACTIVATE
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        
        style = style | WS_EX_NOACTIVATE
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        
        # 再次确认置顶，防止被底层 API 覆盖
        self.root.attributes('-topmost', self.is_pinned)

    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        color = "#3b82f6" if self.is_pinned else "#6b7280"
        self.pin_btn.config(fg=color)
        # 使用 Tkinter 原生方法切换置顶
        self.root.attributes('-topmost', self.is_pinned)

    def toggle_settings(self):
        if self.settings_panel.winfo_ismapped():
            self.settings_panel.pack_forget()
        else:
            self.settings_panel.pack(after=self.header, fill="x")

    def set_alpha(self, value):
        self.root.attributes('-alpha', float(value))

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self.rx = event.x
        self.ry = event.y

    def do_resize(self, event):
        w = self.root.winfo_width() + (event.x - self.rx)
        h = self.root.winfo_height() + (event.y - self.ry)
        if w > 150 and h > 200: # 最小尺寸限制
            self.root.geometry(f"{w}x{h}")

    def on_click(self, key):
        if key == "Enter": keyboard.send("enter")
        elif key == "⌫": keyboard.send("backspace")
        #else: keyboard.write(key)
    
        else: keyboard.send(key) # 改用 send

    def clear_input(self):
        keyboard.send("esc")

if __name__ == "__main__":
    app = FloatingNumpad()
    app.root.mainloop()
