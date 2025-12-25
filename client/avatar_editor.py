"""
像素头像编辑器
"""

import tkinter as tk
import random
import json
import base64


# 头像大小（像素格子数）
AVATAR_SIZE = 16
# 每个格子的显示大小
CELL_SIZE = 12
# 调色板颜色
PALETTE = [
    '#000000', '#FFFFFF', '#FF0000', '#00FF00', '#0000FF',
    '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#800080',
    '#008000', '#000080', '#808080', '#C0C0C0', '#800000',
    '#808000', '#008080', '#FFC0CB', '#FFD700', '#A52A2A'
]


def generate_random_avatar():
    """生成随机像素头像"""
    # 使用对称设计让头像更好看
    pixels = [[None for _ in range(AVATAR_SIZE)] for _ in range(AVATAR_SIZE)]
    
    # 随机选择几个颜色
    colors = random.sample(PALETTE[:10], 3)
    bg_color = random.choice(['#FFFFFF', '#F0F0F0', '#E0E0E0', '#D0D0D0'])
    
    # 填充背景
    for y in range(AVATAR_SIZE):
        for x in range(AVATAR_SIZE):
            pixels[y][x] = bg_color
    
    # 生成左半边，然后镜像到右边（水平对称）
    half = AVATAR_SIZE // 2
    for y in range(2, AVATAR_SIZE - 2):
        for x in range(2, half + 1):
            if random.random() < 0.4:
                color = random.choice(colors)
                pixels[y][x] = color
                pixels[y][AVATAR_SIZE - 1 - x] = color  # 镜像
    
    return pixels


def pixels_to_data(pixels):
    """将像素数据转换为可存储的格式"""
    return json.dumps(pixels)


def data_to_pixels(data):
    """从存储格式恢复像素数据"""
    if not data:
        return generate_random_avatar()
    try:
        return json.loads(data)
    except:
        return generate_random_avatar()


class AvatarEditor(tk.Toplevel):
    """像素头像编辑器窗口"""
    
    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.title("绘制你的头像")
        self.on_complete = on_complete
        self.pixels = [[None for _ in range(AVATAR_SIZE)] for _ in range(AVATAR_SIZE)]
        self.current_color = '#000000'
        self.drawing = False
        
        # 初始化为白色背景
        for y in range(AVATAR_SIZE):
            for x in range(AVATAR_SIZE):
                self.pixels[y][x] = '#FFFFFF'
        
        self.setup_ui()
        
        # 模态窗口
        self.transient(parent)
        self.grab_set()
        
        # 居中显示
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f'+{x}+{y}')
    
    def setup_ui(self):
        from .config import FONT_UI_FAMILY
        
        # Win11 风格配色
        bg_primary = '#202020'
        bg_secondary = '#2d2d2d'
        bg_tertiary = '#383838'
        fg_primary = '#ffffff'
        fg_secondary = '#b3b3b3'
        accent = '#0078d4'
        
        # 字体回退
        ui_font = FONT_UI_FAMILY or 'Microsoft YaHei UI'
        
        self.configure(bg=bg_primary)
        
        # 说明
        tk.Label(
            self, text="绘制你的像素头像", 
            font=(ui_font, 12, 'bold'),
            bg=bg_primary, fg=fg_primary
        ).pack(pady=(15, 10))
        
        main_frame = tk.Frame(self, bg=bg_primary)
        main_frame.pack(padx=15, pady=10)
        
        # 画布容器
        canvas_container = tk.Frame(main_frame, bg=bg_secondary, padx=8, pady=8)
        canvas_container.pack(side='left')
        
        # 画布
        canvas_size = AVATAR_SIZE * CELL_SIZE
        self.canvas = tk.Canvas(
            canvas_container, width=canvas_size, height=canvas_size, 
            bg='#ffffff', highlightthickness=0
        )
        self.canvas.pack()
        
        # 绘制网格
        self.cells = {}
        for y in range(AVATAR_SIZE):
            for x in range(AVATAR_SIZE):
                x1, y1 = x * CELL_SIZE, y * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                rect = self.canvas.create_rectangle(x1, y1, x2, y2, fill='#FFFFFF', outline='#e0e0e0')
                self.cells[(x, y)] = rect
        
        # 鼠标事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<B3-Motion>', self.on_right_drag)
        
        # 右侧面板
        right_panel = tk.Frame(main_frame, bg=bg_primary)
        right_panel.pack(side='left', padx=(15, 0))
        
        # 调色板标题
        tk.Label(
            right_panel, text="调色板", 
            font=(ui_font, 9),
            bg=bg_primary, fg=fg_secondary
        ).pack(pady=(0, 5))
        
        # 调色板容器
        palette_container = tk.Frame(right_panel, bg=bg_secondary, padx=5, pady=5)
        palette_container.pack()
        
        self.color_buttons = []
        palette_grid = tk.Frame(palette_container, bg=bg_secondary)
        palette_grid.pack()
        
        for i, color in enumerate(PALETTE):
            row, col = i // 4, i % 4
            btn = tk.Button(
                palette_grid, bg=color, width=2, height=1,
                relief='flat', bd=0, cursor='hand2',
                command=lambda c=color: self.select_color(c)
            )
            btn.grid(row=row, column=col, padx=1, pady=1)
            self.color_buttons.append(btn)
        
        # 当前颜色显示
        tk.Label(
            right_panel, text="当前颜色", 
            font=(ui_font, 8),
            bg=bg_primary, fg=fg_secondary
        ).pack(pady=(10, 3))
        self.current_color_label = tk.Label(
            right_panel, bg=self.current_color, 
            width=4, height=2, relief='flat'
        )
        self.current_color_label.pack()
        
        # 按钮区
        btn_frame = tk.Frame(self, bg=bg_primary)
        btn_frame.pack(pady=15)
        
        btn_style = {
            'font': (ui_font, 9),
            'relief': 'flat', 'bd': 0,
            'padx': 12, 'pady': 6,
            'cursor': 'hand2'
        }
        
        tk.Button(
            btn_frame, text="🎲 随机", 
            bg=bg_tertiary, fg=fg_primary,
            activebackground='#404040', activeforeground=fg_primary,
            command=self.random_avatar, **btn_style
        ).pack(side='left', padx=3)
        
        tk.Button(
            btn_frame, text="🗑️ 清空", 
            bg=bg_tertiary, fg=fg_primary,
            activebackground='#404040', activeforeground=fg_primary,
            command=self.clear_canvas, **btn_style
        ).pack(side='left', padx=3)
        
        tk.Button(
            btn_frame, text="✓ 确定", 
            bg=accent, fg=fg_primary,
            activebackground='#1a86d9', activeforeground=fg_primary,
            command=self.confirm, **btn_style
        ).pack(side='left', padx=3)
        
        tk.Label(
            self, text="左键绘制  |  右键擦除", 
            font=(ui_font, 8),
            bg=bg_primary, fg=fg_secondary
        ).pack(pady=(0, 10))
    
    def select_color(self, color):
        self.current_color = color
        self.current_color_label.config(bg=color)
    
    def get_cell(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        if 0 <= x < AVATAR_SIZE and 0 <= y < AVATAR_SIZE:
            return x, y
        return None, None
    
    def on_click(self, event):
        x, y = self.get_cell(event)
        if x is not None:
            self.paint_cell(x, y, self.current_color)
    
    def on_drag(self, event):
        x, y = self.get_cell(event)
        if x is not None:
            self.paint_cell(x, y, self.current_color)
    
    def on_right_click(self, event):
        x, y = self.get_cell(event)
        if x is not None:
            self.paint_cell(x, y, '#FFFFFF')
    
    def on_right_drag(self, event):
        x, y = self.get_cell(event)
        if x is not None:
            self.paint_cell(x, y, '#FFFFFF')
    
    def paint_cell(self, x, y, color):
        self.pixels[y][x] = color
        self.canvas.itemconfig(self.cells[(x, y)], fill=color)
    
    def random_avatar(self):
        self.pixels = generate_random_avatar()
        for y in range(AVATAR_SIZE):
            for x in range(AVATAR_SIZE):
                self.canvas.itemconfig(self.cells[(x, y)], fill=self.pixels[y][x])
    
    def clear_canvas(self):
        for y in range(AVATAR_SIZE):
            for x in range(AVATAR_SIZE):
                self.pixels[y][x] = '#FFFFFF'
                self.canvas.itemconfig(self.cells[(x, y)], fill='#FFFFFF')
    
    def confirm(self):
        avatar_data = pixels_to_data(self.pixels)
        self.on_complete(avatar_data)
        self.destroy()


class AvatarDisplay(tk.Canvas):
    """头像显示组件"""
    
    def __init__(self, parent, size=48, **kwargs):
        self.display_size = size
        self.cell_size = size // AVATAR_SIZE
        super().__init__(parent, width=size, height=size, **kwargs)
        self.pixels_data = None
    
    def set_avatar(self, avatar_data):
        """设置并显示头像"""
        self.pixels_data = avatar_data
        pixels = data_to_pixels(avatar_data)
        
        self.delete('all')
        for y in range(AVATAR_SIZE):
            for x in range(AVATAR_SIZE):
                color = pixels[y][x] if pixels[y][x] else '#FFFFFF'
                x1, y1 = x * self.cell_size, y * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
