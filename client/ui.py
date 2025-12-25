"""
UI 组件模块 - WinUI 3 风格
"""

import tkinter as tk
from tkinter import ttk

from .config import (
    COLOR_BG_PRIMARY, COLOR_BG_SECONDARY, COLOR_BG_TERTIARY, COLOR_BG_HOVER,
    COLOR_FG_PRIMARY, COLOR_FG_SECONDARY, COLOR_FG_TERTIARY,
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_ACCENT_LIGHT,
    COLOR_BORDER, COLOR_BORDER_LIGHT,
    COLOR_GAME_BG, COLOR_GAME_FG, COLOR_MAP_BG, COLOR_MAP_FG,
    COLOR_STATUS_BG, COLOR_STATUS_FG, COLOR_INPUT_BG,
    FONT_UI_FAMILY, FONT_MONO_FAMILY,
    RADIUS_SMALL, RADIUS_MEDIUM, RADIUS_LARGE, RADIUS_XLARGE,
    PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE, PADDING_XLARGE,
    UI_SCALE
)
from .avatar_editor import AvatarDisplay, data_to_pixels, AVATAR_SIZE

# 统一UI字体
UI_FONT = 'Microsoft YaHei UI'


# 麻将牌桌颜色 - 使用主题色
COLOR_TABLE_BG = COLOR_BG_TERTIARY
COLOR_TABLE_BORDER = COLOR_BORDER
COLOR_SEAT_EMPTY = COLOR_BG_SECONDARY
COLOR_SEAT_OCCUPIED = COLOR_ACCENT


# ============ WinUI 3 风格组件 ============

class RoundedFrame(tk.Canvas):
    """圆角边框容器 - 模拟 WinUI 3 卡片"""
    
    def __init__(self, parent, radius=None, bg=COLOR_BG_SECONDARY, border_color=COLOR_BORDER, **kwargs):
        super().__init__(parent, highlightthickness=0, bg=COLOR_BG_PRIMARY, **kwargs)
        self.radius = radius if radius is not None else RADIUS_MEDIUM
        self.bg_color = bg
        self.border_color = border_color
        
        # 内部容器
        self.inner = tk.Frame(self, bg=bg)
        self.inner_window = self.create_window(0, 0, window=self.inner, anchor='nw')
        
        self.bind('<Configure>', self._on_resize)
    
    def _on_resize(self, event):
        w, h = event.width, event.height
        r = self.radius
        
        self.delete('bg')
        
        # 绘制圆角矩形
        self.create_rounded_rect(1, 1, w-2, h-2, r, fill=self.bg_color, outline=self.border_color, tags='bg')
        self.tag_lower('bg')
        
        # 调整内部容器大小
        self.itemconfig(self.inner_window, width=w-4, height=h-4)
        self.coords(self.inner_window, 2, 2)
    
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """绘制圆角矩形"""
        points = [
            x1+r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y1+r,
            x1, y1,
            x1+r, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class ModernScrolledText(tk.Frame):
    """现代滚动文本框 - WinUI 3 风格滚动条"""
    
    def __init__(self, parent, font=None, width=30, height=10, 
                 bg=COLOR_BG_TERTIARY, fg=COLOR_FG_PRIMARY, wrap='word', **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        # 文本框
        self.text = tk.Text(
            self, font=font, width=width, height=height,
            bg=bg, fg=fg, wrap=wrap,
            relief='flat', bd=0, padx=10, pady=10,
            insertbackground=fg, selectbackground=COLOR_ACCENT,
            selectforeground=COLOR_FG_PRIMARY
        )
        self.text.grid(row=0, column=0, sticky='nsew')
        
        # 自定义滚动条
        self.scrollbar = ModernScrollbar(self, command=self.text.yview)
        self.scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 2), pady=2)
        
        self.text.configure(yscrollcommand=self.scrollbar.set)
    
    def config(self, **kwargs):
        if 'state' in kwargs:
            self.text.config(state=kwargs['state'])
    
    def insert(self, index, chars, *args):
        self.text.insert(index, chars, *args)
    
    def delete(self, index1, index2=None):
        self.text.delete(index1, index2)
    
    def see(self, index):
        self.text.see(index)
    
    def tag_config(self, tagName, **kwargs):
        self.text.tag_config(tagName, **kwargs)


class ModernScrollbar(tk.Canvas):
    """现代滚动条 - WinUI 3 风格"""
    
    def __init__(self, parent, command=None, **kwargs):
        super().__init__(parent, width=8, highlightthickness=0, bg=COLOR_BG_TERTIARY, **kwargs)
        self.command = command
        
        self.thumb_color = COLOR_FG_TERTIARY
        self.thumb_hover = COLOR_FG_SECONDARY
        
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<Enter>', lambda e: self._set_thumb_color(self.thumb_hover))
        self.bind('<Leave>', lambda e: self._set_thumb_color(self.thumb_color))
        
        self._thumb_pos = (0, 1)
        self._drag_start = None
    
    def set(self, lo, hi):
        lo, hi = float(lo), float(hi)
        self._thumb_pos = (lo, hi)
        self._draw_thumb()
    
    def _draw_thumb(self):
        self.delete('thumb')
        w = self.winfo_width()
        h = self.winfo_height()
        
        lo, hi = self._thumb_pos
        if hi - lo >= 1:
            return  # 不需要滚动条
        
        y1 = int(lo * h) + 2
        y2 = int(hi * h) - 2
        
        if y2 - y1 < 20:
            y2 = y1 + 20
        
        # 绘制圆角滑块 - Win11风格更圆润
        self.create_rounded_thumb(2, y1, w-2, y2, RADIUS_SMALL, fill=self.thumb_color, tags='thumb')
    
    def create_rounded_thumb(self, x1, y1, x2, y2, r, **kwargs):
        r = min(r, (x2-x1)//2, (y2-y1)//2)
        if r < 2:
            r = 2
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1, x1+r, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _set_thumb_color(self, color):
        self.thumb_color = color
        self.itemconfig('thumb', fill=color)
    
    def _on_press(self, event):
        h = self.winfo_height()
        lo, hi = self._thumb_pos
        
        y1 = lo * h
        y2 = hi * h
        
        if y1 <= event.y <= y2:
            self._drag_start = event.y
        else:
            # 点击空白区域，跳转
            ratio = event.y / h
            if self.command:
                self.command('moveto', ratio)
    
    def _on_drag(self, event):
        if self._drag_start is None:
            return
        
        h = self.winfo_height()
        delta = (event.y - self._drag_start) / h
        
        if self.command:
            self.command('moveto', self._thumb_pos[0] + delta)
        self._drag_start = event.y


class ModernButton(tk.Canvas):
    """WinUI 3 风格按钮 - 大尺寸、圆角、悬停效果"""
    
    def __init__(self, parent, text="", command=None, accent=False,
                 width=140, height=48, font=None, icon=None, **kwargs):
        # 设置画布背景与父容器一致
        parent_bg = parent.cget('bg') if hasattr(parent, 'cget') else COLOR_BG_SECONDARY
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent_bg, **kwargs)
        
        self._text = text
        self.command = command
        self.accent = accent
        self.icon = icon
        self._width = width
        self._height = height
        self.font = font or ('Microsoft YaHei UI', 10)
        
        # 颜色配置
        self.bg_normal = COLOR_ACCENT if accent else COLOR_BG_TERTIARY
        self.bg_hover = COLOR_ACCENT_HOVER if accent else '#3d3d3d'
        self.bg_press = '#005a9e' if accent else '#4d4d4d'
        self.fg_color = COLOR_FG_PRIMARY
        self.parent_bg = parent_bg
        
        self._pressed = False
        self._hovered = False
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self.bind('<Configure>', lambda e: self._draw())
        
        self._draw()
    
    def _draw(self, bg=None):
        self.delete('all')
        w = self.winfo_width() if self.winfo_width() > 1 else self._width
        h = self.winfo_height() if self.winfo_height() > 1 else self._height
        r = RADIUS_MEDIUM  # Win11风格圆角
        
        if bg is None:
            bg = self.bg_normal
        
        # 绘制圆角矩形背景
        self._create_rounded_rect(0, 0, w, h, r, fill=bg, outline='')
        
        # 计算文字位置 - 对于+等符号微调向上偏移
        text_x = w // 2
        text_y = h // 2
        # 如果是单字符符号，微调位置使其视觉居中
        if len(self._text) == 1 and self._text in '+-×✕＋':
            text_y = h // 2 - 2
        
        # 绘制文字
        self.create_text(text_x, text_y, text=self._text, 
                        fill=self.fg_color, font=self.font, anchor='center')
    
    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """绘制圆角矩形 - 使用多点模拟圆弧确保圆角对称"""
        import math
        
        # 确保圆角半径不超过矩形的一半
        r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
        
        points = []
        # 每个圆角用多个点来模拟
        steps = 8  # 每个圆角的点数
        
        # 左上角圆弧 (180° 到 270°)
        for i in range(steps + 1):
            angle = math.pi + (math.pi / 2) * i / steps
            px = x1 + r + r * math.cos(angle)
            py = y1 + r + r * math.sin(angle)
            points.extend([px, py])
        
        # 右上角圆弧 (270° 到 360°)
        for i in range(steps + 1):
            angle = 1.5 * math.pi + (math.pi / 2) * i / steps
            px = x2 - r + r * math.cos(angle)
            py = y1 + r + r * math.sin(angle)
            points.extend([px, py])
        
        # 右下角圆弧 (0° 到 90°)
        for i in range(steps + 1):
            angle = (math.pi / 2) * i / steps
            px = x2 - r + r * math.cos(angle)
            py = y2 - r + r * math.sin(angle)
            points.extend([px, py])
        
        # 左下角圆弧 (90° 到 180°)
        for i in range(steps + 1):
            angle = math.pi / 2 + (math.pi / 2) * i / steps
            px = x1 + r + r * math.cos(angle)
            py = y2 - r + r * math.sin(angle)
            points.extend([px, py])
        
        return self.create_polygon(points, smooth=False, **kwargs)
    
    def _on_enter(self, event):
        self._hovered = True
        self.configure(cursor='hand2')
        self._draw(self.bg_hover)
    
    def _on_leave(self, event):
        self._hovered = False
        self._draw(self.bg_normal)
    
    def _on_press(self, event):
        self._pressed = True
        self._draw(self.bg_press)
    
    def _on_release(self, event):
        if self._pressed and self.command:
            self.command()
        self._pressed = False
        # 检查组件是否仍然存在
        try:
            if self._hovered:
                self._draw(self.bg_hover)
            else:
                self._draw(self.bg_normal)
        except tk.TclError:
            pass  # 组件已销毁


class NavButton(tk.Canvas):
    """WinUI 3 导航按钮 - 类似设置页左侧菜单项"""
    
    def __init__(self, parent, text="", command=None, selected=False,
                 width=180, height=56, font=None, **kwargs):
        parent_bg = COLOR_BG_SECONDARY
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent_bg, **kwargs)
        
        self._text = text
        self.command = command
        self._selected = selected
        self._width = width
        self._height = height
        self.font = font or ('Microsoft YaHei UI', 12)
        self.parent_bg = parent_bg
        
        # 颜色
        self.bg_normal = parent_bg
        self.bg_hover = '#3a3a3a'
        self.bg_selected = '#3a3a3a'
        self.accent_color = COLOR_ACCENT
        
        self._hovered = False
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_press)
        
        self._draw()
    
    def set_selected(self, selected):
        self._selected = selected
        try:
            self._draw()
        except tk.TclError:
            pass
    
    def _draw(self):
        self.delete('all')
        w = self._width
        h = self._height
        r = RADIUS_MEDIUM  # Win11风格圆角
        
        # 背景色
        if self._selected:
            bg = self.bg_selected
        elif self._hovered:
            bg = self.bg_hover
        else:
            bg = self.bg_normal
        
        # 绘制圆角矩形背景
        self._create_rounded_rect(2, 2, w-2, h-2, r, fill=bg, outline='')
        
        # 选中时绘制左侧高亮条（WinUI 风格）
        if self._selected:
            bar_height = 22
            bar_y = (h - bar_height) // 2
            self._create_rounded_rect(5, bar_y, 9, bar_y + bar_height, RADIUS_SMALL, 
                                      fill=self.accent_color, outline='')
        
        # 文字（稍微右移为高亮条留空间）
        text_x = 24 if self._selected else 18
        self.create_text(text_x, h//2, text=self._text, 
                        fill=COLOR_FG_PRIMARY, font=self.font, anchor='w')
    
    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        r = min(r, (x2-x1)/2, (y2-y1)/2)
        if r < 1:
            return self.create_rectangle(x1, y1, x2, y2, **kwargs)
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1, x1+r, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        self._hovered = True
        self.configure(cursor='hand2')
        self._draw()
    
    def _on_leave(self, event):
        self._hovered = False
        self._draw()
    
    def _on_press(self, event):
        if self.command:
            self.command()


class MahjongTableView(tk.Canvas):
    """麻将弃牌堆视图 - 显示4个玩家的弃牌堆，支持滚动"""
    
    POSITIONS = ['东', '南', '西', '北']
    WIND_COLORS = {
        '东': '#4CAF50',  # 绿色
        '南': '#2196F3',  # 蓝色
        '西': '#FF9800',  # 橙色
        '北': '#9C27B0',  # 紫色
    }
    
    # 牌类型颜色
    TILE_COLORS = {
        '万': '#FF6B6B',  # 万子 - 红色
        '条': '#7ED321',  # 条子 - 绿色
        '筒': '#5DADE2',  # 筒子 - 蓝色
        '风': '#F7DC6F',  # 风牌 - 黄色
        '元': '#BB8FCE',  # 三元牌 - 紫色
    }
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, bg=COLOR_BG_SECONDARY, **kwargs)
        self.room_data = None
        self.scroll_offsets = [0, 0, 0, 0]  # 每列独立滚动偏移量
        self.max_scrolls = [0, 0, 0, 0]  # 每列最大滚动量
        self.hover_col = -1  # 鼠标悬停的列
        
        self.bind('<Configure>', self._on_resize)
        self.bind('<MouseWheel>', self._on_mousewheel)
        self.bind('<Button-4>', self._on_mousewheel)  # Linux
        self.bind('<Button-5>', self._on_mousewheel)  # Linux
        self.bind('<Motion>', self._on_motion)
    
    def _get_tile_color_for_canvas(self, tile):
        """根据牌的类型返回颜色"""
        if '万' in tile:
            return self.TILE_COLORS['万']
        elif '条' in tile:
            return self.TILE_COLORS['条']
        elif '筒' in tile:
            return self.TILE_COLORS['筒']
        elif tile in ['东', '南', '西', '北']:
            return self.TILE_COLORS['风']
        elif tile in ['中', '发', '白']:
            return self.TILE_COLORS['元']
        else:
            return COLOR_FG_SECONDARY
    
    def _on_motion(self, event):
        """跟踪鼠标位置，确定悬停在哪一列"""
        w = self.winfo_width()
        padding = 6
        col_w = (w - padding * 2 - 18) // 4
        start_x = padding
        
        for i in range(4):
            col_x = start_x + i * (col_w + 6)
            if col_x <= event.x <= col_x + col_w:
                self.hover_col = i
                return
        self.hover_col = -1
    
    def _on_mousewheel(self, event):
        """鼠标滚轮滚动 - 只滚动悬停的列"""
        if self.hover_col < 0 or self.hover_col >= 4:
            return
        if self.max_scrolls[self.hover_col] <= 0:
            return
        
        # Windows: event.delta, Linux: Button-4/5
        if hasattr(event, 'delta'):
            delta = -event.delta // 120 * 32
        elif event.num == 4:
            delta = -32
        else:
            delta = 32
        
        self.scroll_offsets[self.hover_col] = max(0, min(
            self.max_scrolls[self.hover_col], 
            self.scroll_offsets[self.hover_col] + delta
        ))
        self._redraw()
    
    def _on_resize(self, event):
        """窗口大小改变时重绘"""
        self._redraw()
    
    def _redraw(self):
        """重绘弃牌堆"""
        if self.room_data:
            self._draw_discard_piles(self.room_data)
        else:
            self._draw_empty()
    
    def _draw_empty(self):
        """绘制空状态"""
        self.delete('all')
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return
        
        # 绘制等待加入房间提示
        self.create_text(w//2, h//2, text="🀄 等待加入房间", 
                        font=(UI_FONT, 14), fill=COLOR_FG_TERTIARY)
    
    def _draw_discard_piles(self, room_data):
        """绘制弃牌堆视图 - 4列，每列一个玩家"""
        self.delete('all')
        self.max_scrolls = [0, 0, 0, 0]  # 重置每列最大滚动量
        
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return
        
        positions = room_data.get('positions', [])
        state = room_data.get('state', 'waiting')
        current_turn = room_data.get('current_turn', -1)
        deck_remaining = room_data.get('deck_remaining', 0)
        last_discard = room_data.get('last_discard')
        
        # 标题栏 - 只显示房间号（场风和宝牌移到状态窗口）
        title_h = 20
        self._create_rounded_rect(4, 2, w-4, title_h + 2, RADIUS_MEDIUM,
                                 fill=COLOR_BG_TERTIARY, outline=COLOR_BORDER)
        
        # 房间号
        room_id = room_data.get('room_id', '')
        if room_id:
            short_id = room_id[-4:] if len(room_id) > 4 else room_id
            if state == 'waiting':
                self.create_text(w//2, 12, text=f"房间 #{short_id} - 等待中",
                                font=(UI_FONT, 9), fill=COLOR_FG_TERTIARY)
            else:
                deck_remaining = room_data.get('deck_remaining', 0)
                self.create_text(w//2, 12, text=f"#{short_id} | 剩{deck_remaining}张",
                                font=(UI_FONT, 9), fill=COLOR_FG_TERTIARY)
        
        # 4个玩家列
        padding = 6
        col_w = (w - padding * 2 - 18) // 4  # 列之间留空隙
        start_x = padding
        start_y = title_h + 8
        content_h = h - start_y - 6
        
        # 固定头部区域高度 - 风位(20+8) + 头像(48+10) + 名字(12+16) + 分数(12+14) + 立直(12) = 152
        header_h = 150
        
        for i in range(4):
            x = start_x + i * (col_w + 6)
            
            # 获取玩家数据 - positions已按东南西北排序
            if i < len(positions):
                pos_data = positions[i]
                player_name = pos_data.get('name')
                is_turn = pos_data.get('is_turn', False)
                discards = pos_data.get('discards', [])
                avatar_data = pos_data.get('avatar')
                melds = pos_data.get('melds', [])  # 副露
                is_riichi = pos_data.get('is_riichi', False)  # 立直状态
                is_dealer = pos_data.get('is_dealer', False)  # 庄家
                score = pos_data.get('score', 25000)  # 分数
                player_wind = pos_data.get('wind', self.POSITIONS[i])  # 自风
            else:
                player_name = None
                is_turn = False
                discards = []
                avatar_data = None
                melds = []
                is_riichi = False
                is_dealer = False
                score = 25000
                player_wind = self.POSITIONS[i]  # 默认使用座位作为风位
            
            # 列背景
            col_right = x + col_w
            if is_turn and state == 'playing':
                self._create_rounded_rect(x, start_y, col_right, start_y + content_h, RADIUS_MEDIUM,
                                         fill='#2d3748', outline=COLOR_ACCENT, width=2)
            else:
                self._create_rounded_rect(x, start_y, col_right, start_y + content_h, RADIUS_MEDIUM,
                                         fill=COLOR_BG_TERTIARY, outline=COLOR_BORDER)
            
            col_center = x + col_w // 2
            
            # === 头部区域（固定位置） ===
            # 风位标识 - 使用玩家的自风
            wind_y = start_y + 6
            wind_size = 20
            display_wind = player_wind if player_wind else self.POSITIONS[i]
            wind_display_color = self.WIND_COLORS.get(display_wind, '#666666')
            self.create_oval(col_center - wind_size//2, wind_y,
                           col_center + wind_size//2, wind_y + wind_size,
                           fill=wind_display_color, outline='')
            self.create_text(col_center, wind_y + wind_size//2,
                           text=display_wind, font=(UI_FONT, 10, 'bold'), fill='white')
            
            # 头像 - 48px
            avatar_y = wind_y + wind_size + 8
            avatar_size = 48
            if player_name:
                if avatar_data:
                    self._draw_mini_avatar(col_center, avatar_y + avatar_size//2, avatar_data, avatar_size)
                else:
                    self.create_text(col_center, avatar_y + avatar_size//2,
                                   text="👤", font=(UI_FONT, 20), fill=COLOR_FG_SECONDARY)
                
                # 玩家名 - 在头像底部下方14px
                name_y = avatar_y + avatar_size + 14
                display_name = player_name[:6] if len(player_name) > 6 else player_name
                self.create_text(col_center, name_y,
                               text=display_name, font=(UI_FONT, 8),
                               fill=COLOR_ACCENT if is_turn else COLOR_FG_PRIMARY)
                
                # 分数显示 - 在名字下方22px
                score_y = name_y + 22
                score_text = f"{score:,}"
                self.create_text(col_center, score_y,
                               text=score_text, font=(UI_FONT, 8),
                               fill='#FFD700' if score >= 25000 else '#FF6B6B')
                
                # 立直状态 - 使用立直棒表示
                if is_riichi:
                    riichi_y = score_y + 14
                    # 立直棒：━ 或 ─ 来模拟
                    self.create_text(col_center, riichi_y,
                                   text="━━━", font=(UI_FONT, 10, 'bold'),
                                   fill='#FF4444')
            else:
                self.create_text(col_center, avatar_y + avatar_size//2,
                               text="空位", font=(UI_FONT, 10), fill=COLOR_FG_TERTIARY)
            
            # === 弃牌区域（固定从 header_h 开始） ===
            discard_start_y = start_y + header_h
            
            # 分隔线
            self.create_line(x + 8, discard_start_y - 6, col_right - 8, discard_start_y - 6, 
                           fill=COLOR_BORDER, width=1)
            
            # 计算总内容高度（副露 + 弃牌）
            tile_h = 28  # 行高
            content_items = []  # [(type, data), ...] - 'meld' or 'discard'
            
            # 添加副露内容
            for meld in melds:
                meld_type = meld.get('type', '')
                tiles = meld.get('tiles', [])
                # 支持暗杠类型
                type_text = {
                    'pong': '碰', 
                    'kong': '杠', 
                    'chow': '吃',
                    'concealed_kong': '暗杠'
                }.get(meld_type, '')
                type_color = {
                    'pong': '#FF5722', 
                    'kong': '#9C27B0', 
                    'chow': '#4CAF50',
                    'concealed_kong': '#E91E63'
                }.get(meld_type, COLOR_ACCENT)
                
                # 类型标记行
                content_items.append(('meld_type', {'text': f'[{type_text}]', 'color': type_color}))
                # 每张牌单独一行（暗杠显示为"🀫"表示暗牌）
                if meld_type == 'concealed_kong':
                    # 暗杠只显示牌名，表示这是暗的
                    tile_name = tiles[0] if tiles else '?'
                    content_items.append(('meld_tile', {'text': f'🀫{tile_name}×4', 'color': type_color}))
                else:
                    for tile in tiles[:4]:
                        content_items.append(('meld_tile', {'text': tile, 'color': type_color}))
            
            # 添加分隔标记
            if melds:
                content_items.append(('separator', None))
            
            # 添加弃牌
            for j, tile in enumerate(discards):
                is_last = (j == len(discards) - 1) and last_discard and (tile == last_discard)
                content_items.append(('discard', {'text': tile, 'is_last': is_last}))
            
            # 计算可见区域和滚动
            available_h = start_y + content_h - discard_start_y - 10
            total_height = len(content_items) * tile_h
            col_max_scroll = max(0, total_height - available_h)
            self.max_scrolls[i] = col_max_scroll
            
            scroll_offset = self.scroll_offsets[i]
            
            # 绘制内容
            for idx, item in enumerate(content_items):
                ty = discard_start_y + idx * tile_h - scroll_offset
                
                # 只绘制可见区域内的内容
                if ty + tile_h < discard_start_y - 5:
                    continue
                if ty > start_y + content_h - 5:
                    continue
                
                item_type, data = item
                
                if item_type == 'meld_type':
                    self.create_text(col_center, ty + tile_h//2,
                                   text=data['text'],
                                   font=(UI_FONT, 9, 'bold'), fill=data['color'])
                elif item_type == 'meld_tile':
                    self.create_text(col_center, ty + tile_h//2,
                                   text=data['text'],
                                   font=(UI_FONT, 9), fill=data['color'])
                elif item_type == 'separator':
                    self.create_line(x + 8, ty + tile_h//2, col_right - 8, ty + tile_h//2, 
                                   fill=COLOR_BORDER, dash=(2, 2), width=1)
                elif item_type == 'discard':
                    # 最后一张打出的牌用强调色，其他按牌类型上色
                    if data['is_last']:
                        tile_color = COLOR_ACCENT
                    else:
                        tile_color = self._get_tile_color_for_canvas(data['text'])
                    self.create_text(col_center, ty + tile_h//2,
                                   text=data['text'], font=(UI_FONT, 10),
                                   fill=tile_color)
            
            # 如果可以滚动，显示滚动条
            if col_max_scroll > 0:
                # 计算滚动条位置
                scrollbar_h = max(20, available_h * available_h / total_height)
                scrollbar_y = discard_start_y + (available_h - scrollbar_h) * scroll_offset / col_max_scroll
                
                # 绘制滚动条轨道
                self.create_rectangle(col_right - 6, discard_start_y, col_right - 2, discard_start_y + available_h,
                                     fill=COLOR_BG_TERTIARY, outline='')
                # 绘制滚动条
                self.create_rectangle(col_right - 5, scrollbar_y, col_right - 3, scrollbar_y + scrollbar_h,
                                     fill=COLOR_FG_TERTIARY, outline='')
    
    def _draw_mini_avatar(self, x, y, avatar_data, size):
        """绘制迷你像素头像"""
        if not avatar_data:
            return
        
        # 检查是否是机器人生成的颜色头像
        if isinstance(avatar_data, dict) and avatar_data.get('type') == 'generated':
            color = avatar_data.get('color', '#4A90A4')
            # 绘制一个带颜色的圆形作为头像
            self.create_oval(x - size//2, y - size//2,
                           x + size//2, y + size//2,
                           fill=color, outline='#333333', width=1)
            # 添加机器人图标
            self.create_text(x, y, text='🤖', font=(UI_FONT, size//3))
            return
        
        pixels = data_to_pixels(avatar_data)
        if not pixels:
            return
        
        pixel_size = max(1, size // AVATAR_SIZE)
        start_x = x - size // 2
        start_y = y - size // 2
        
        for py, row in enumerate(pixels):
            for px, color in enumerate(row):
                if color:
                    rx = start_x + px * pixel_size
                    ry = start_y + py * pixel_size
                    self.create_rectangle(rx, ry, rx + pixel_size, ry + pixel_size,
                                        fill=color, outline='')
    
    def update_table(self, room_data):
        """更新弃牌堆显示"""
        self.room_data = room_data
        self._redraw()
    
    def clear(self):
        """清空显示"""
        self.room_data = None
        self._draw_empty()
    
    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """绘制圆角矩形"""
        r = min(r, (x2-x1)/2, (y2-y1)/2)
        if r < 1:
            return self.create_rectangle(x1, y1, x2, y2, **kwargs)
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1, x1+r, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)


class ModernEntry(tk.Frame):
    """现代输入框 - WinUI 3 风格，带底部边框"""
    
    def __init__(self, parent, font=None, width=30, **kwargs):
        super().__init__(parent, bg=COLOR_BG_TERTIARY, **kwargs)
        
        self.entry = tk.Entry(
            self, font=font, width=width,
            bg=COLOR_BG_TERTIARY, fg=COLOR_FG_PRIMARY,
            insertbackground=COLOR_FG_PRIMARY,
            relief='flat', bd=0, selectbackground=COLOR_ACCENT
        )
        self.entry.pack(fill='x', ipady=8, ipadx=10)
        
        # 底部边框
        self.border = tk.Frame(self, height=2, bg=COLOR_BORDER)
        self.border.pack(fill='x')
        
        # 聚焦效果
        self.entry.bind('<FocusIn>', lambda e: self.border.configure(bg=COLOR_ACCENT))
        self.entry.bind('<FocusOut>', lambda e: self.border.configure(bg=COLOR_BORDER))
    
    def get(self):
        return self.entry.get()
    
    def delete(self, first, last=None):
        self.entry.delete(first, last)
    
    def insert(self, index, string):
        self.entry.insert(index, string)
    
    def bind(self, sequence, func):
        self.entry.bind(sequence, func)
    
    def focus(self):
        self.entry.focus_set()


class LoginUI:
    """登录界面 - WinUI 3 风格"""
    
    def __init__(self, root, on_connect):
        self.root = root
        self.on_connect = on_connect
        self.frame = None
        self.ip_entry = None
        
        root.configure(bg=COLOR_BG_PRIMARY)
        
        self.setup()
    
    def setup(self):
        from .config import FONT_CHAT, FONT_BUTTON, FONT_LABEL, FONT_TITLE, DEFAULT_HOST
        
        # 主容器
        self.frame = tk.Frame(self.root, bg=COLOR_BG_PRIMARY, padx=60, pady=60)
        self.frame.pack(expand=True)
        
        # 标题
        title = tk.Label(
            self.frame, text="🎮 游戏大厅", 
            font=FONT_TITLE,
            bg=COLOR_BG_PRIMARY, fg=COLOR_FG_PRIMARY
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 40))
        
        # 卡片容器 (使用 RoundedFrame)
        card_container = RoundedFrame(self.frame, width=420, height=260, radius=RADIUS_LARGE)
        card_container.grid(row=1, column=0, columnspan=2)
        card = card_container.inner
        card.configure(padx=35, pady=30)
        
        # 服务器IP标签
        tk.Label(
            card, text="服务器地址", font=FONT_LABEL,
            bg=COLOR_BG_SECONDARY, fg=COLOR_FG_SECONDARY
        ).pack(anchor='w', pady=(0, 12))
        
        # IP输入框
        self.ip_entry = ModernEntry(card, font=FONT_CHAT, width=30)
        self.ip_entry.pack(fill='x')
        self.ip_entry.insert(0, DEFAULT_HOST)
        
        # 连接按钮 - 居中显示
        btn_frame = tk.Frame(card, bg=COLOR_BG_SECONDARY)
        btn_frame.pack(fill='x', pady=(30, 0))
        
        connect_btn = ModernButton(
            btn_frame, text="连接服务器", accent=True,
            width=350, height=52, font=FONT_BUTTON,
            command=self._on_connect
        )
        connect_btn.pack(anchor='center')
        
        self.ip_entry.bind('<Return>', lambda e: self._on_connect())
    
    def _on_connect(self):
        ip = self.ip_entry.get().strip() or DEFAULT_HOST
        self.on_connect(ip)
    
    def destroy(self):
        self.frame.destroy()


class GameUI:
    """游戏主界面 - WinUI 3 风格"""
    
    def __init__(self, root, on_chat, on_command, on_switch_channel):
        self.root = root
        self.on_chat = on_chat
        self.on_command = on_command
        self.on_switch_channel = on_switch_channel
        
        # 聊天室相关
        self.current_channel = 1
        self.channels = {1: "频道1", 2: "频道2"}
        self.online_users = []
        self.logged_in = False
        self.in_mahjong_game = False  # 是否在麻将游戏中
        self.current_location = 'lobby'  # 当前位置
        self.current_room_id = None  # 当前房间ID
        
        # 位置名称映射（不包含房间，房间需要特殊处理显示ID）
        self.location_names = {
            'lobby': '游戏大厅',
            'profile': '个人资料',
            'jrpg': 'JRPG',
            'mahjong': '麻将',
            'mahjong_room': '房间',
            'mahjong_playing': '对局中'
        }
        
        # UI组件
        self.channel_buttons = {}
        self.online_label = None
        self.chat_area = None
        self.game_area = None
        self.map_text = None
        self.status_text = None
        self.chat_entry = None
        self.cmd_entry = None
        
        # 游戏状态缓存
        self._cached_player_data = None
        self._cached_room_data = None
        self.current_hand = None
        self.drawn_tile = None
        self.tenpai_analysis = None
        self.cmd_history_temp = ''
        self.need_discard = False  # 是否需要打牌（轮到自己出牌）
        
        self.setup()
    
    def setup(self):
        from .config import FONT_CHAT, FONT_GAME, FONT_MAP, FONT_STATUS, FONT_BUTTON, FONT_LABEL
        
        self.root.configure(bg=COLOR_BG_PRIMARY)
        
        main_frame = tk.Frame(self.root, bg=COLOR_BG_PRIMARY)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        self._setup_chat_panel(main_frame)
        self._setup_command_panel(main_frame)
        self._setup_info_panel(main_frame)
        
        self.update_map(None)
        self.update_status(None)
        self.cmd_entry.focus()
    
    def _setup_chat_panel(self, parent):
        from .config import FONT_CHAT, FONT_BUTTON, FONT_LABEL
        
        # 左侧圆角卡片
        left_card = RoundedFrame(parent, radius=RADIUS_MEDIUM)
        left_card.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        inner = left_card.inner
        inner.rowconfigure(2, weight=1)
        inner.columnconfigure(0, weight=1)
        
        # 频道选择按钮（WinUI 导航风格）
        channel_frame = tk.Frame(inner, bg=COLOR_BG_SECONDARY)
        channel_frame.grid(row=0, column=0, sticky='ew', padx=8, pady=(10, 6))
        
        for ch_id, ch_name in self.channels.items():
            btn = NavButton(
                channel_frame, text=ch_name, width=140, height=52,
                font=FONT_BUTTON, selected=(ch_id == self.current_channel),
                command=lambda c=ch_id: self._switch_channel(c)
            )
            btn.pack(side='left', padx=3)
            self.channel_buttons[ch_id] = btn
        
        # 在线用户显示（使用Text组件以支持不同样式）
        self.online_text = tk.Text(
            inner, height=1, wrap='none',
            font=FONT_LABEL, bg=COLOR_BG_SECONDARY, fg=COLOR_FG_TERTIARY,
            relief='flat', bd=0, padx=12, pady=3, state='disabled',
            cursor='arrow'
        )
        self.online_text.grid(row=1, column=0, sticky='ew', padx=0, pady=3)
        self.online_text.tag_config('prefix', foreground=COLOR_FG_TERTIARY)
        self.online_text.tag_config('bold', foreground=COLOR_FG_PRIMARY, font=(FONT_LABEL[0], FONT_LABEL[1], 'bold'))
        self.online_text.tag_config('dim', foreground='#666666')
        # 兼容旧代码
        self.online_label = self.online_text
        
        # 聊天区域（使用自定义滚动文本框）
        chat_container = tk.Frame(inner, bg=COLOR_BG_SECONDARY)
        chat_container.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
        chat_container.rowconfigure(0, weight=1)
        chat_container.columnconfigure(0, weight=1)
        
        self.chat_area = ModernScrolledText(
            chat_container, font=FONT_CHAT, width=25,
            bg=COLOR_BG_TERTIARY, fg=COLOR_FG_PRIMARY
        )
        self.chat_area.grid(row=0, column=0, sticky='nsew')
        self.chat_area.tag_config('system', foreground=COLOR_FG_TERTIARY)
        self.chat_area.tag_config('chat', foreground=COLOR_FG_PRIMARY)
        self.chat_area.tag_config('time', foreground='#666666', font=(UI_FONT, 7))  # 时间：小灰色字体
        self.chat_area.tag_config('name', foreground=COLOR_ACCENT)  # 名字：主题色
        
        # 聊天输入框
        chat_input_frame = tk.Frame(inner, bg=COLOR_BG_SECONDARY)
        chat_input_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(5, 10))
        chat_input_frame.columnconfigure(0, weight=1)
        
        self.chat_entry = ModernEntry(chat_input_frame, font=FONT_CHAT)
        self.chat_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        self.chat_entry.bind('<Return>', lambda e: self._send_chat())
        
        send_btn = ModernButton(
            chat_input_frame, text="发送", accent=True,
            width=100, height=48, font=FONT_BUTTON,
            command=self._send_chat
        )
        send_btn.grid(row=0, column=1)
    
    def _setup_command_panel(self, parent):
        from .config import FONT_GAME, FONT_BUTTON, FONT_LABEL
        
        # 中间圆角卡片
        mid_card = RoundedFrame(parent, radius=RADIUS_MEDIUM)
        mid_card.grid(row=0, column=1, sticky='nsew', padx=5)
        
        inner = mid_card.inner
        inner.rowconfigure(1, weight=1)
        inner.columnconfigure(0, weight=1)
        
        # 指令窗口标签栏（和聊天室频道一样的布局）
        tab_outer_frame = tk.Frame(inner, bg=COLOR_BG_SECONDARY)
        tab_outer_frame.grid(row=0, column=0, sticky='ew', padx=8, pady=(10, 6))
        tab_outer_frame.columnconfigure(0, weight=1)
        
        # 右侧：+ 按钮（固定在右边，先pack确保空间）
        self.add_tab_btn = ModernButton(
            tab_outer_frame, text="+", accent=False,
            width=52, height=52, font=(UI_FONT, 20),
            command=self._create_cmd_window
        )
        self.add_tab_btn.pack(side='right', padx=(5, 0), pady=0)
        
        # 左侧：标签容器（可滚动）
        tab_scroll_frame = tk.Frame(tab_outer_frame, bg=COLOR_BG_SECONDARY)
        tab_scroll_frame.pack(side='left', fill='x', expand=True)
        
        # 使用Canvas实现水平滚动
        self.cmd_tab_canvas = tk.Canvas(tab_scroll_frame, bg=COLOR_BG_SECONDARY, 
                                         height=52, highlightthickness=0)
        self.cmd_tab_canvas.pack(side='top', fill='x', expand=True)
        
        self.cmd_tab_frame = tk.Frame(self.cmd_tab_canvas, bg=COLOR_BG_SECONDARY)
        self.cmd_tab_window = self.cmd_tab_canvas.create_window((0, 0), window=self.cmd_tab_frame, anchor='nw')
        
        # 水平滚动条（使用自定义暗色滚动条）
        self.cmd_tab_scrollbar_frame = tk.Frame(tab_scroll_frame, bg=COLOR_BG_TERTIARY, height=8)
        self.cmd_tab_scrollbar = tk.Canvas(self.cmd_tab_scrollbar_frame, bg=COLOR_BG_TERTIARY, 
                                            height=8, highlightthickness=0)
        self.cmd_tab_scrollbar.pack(fill='x', expand=True)
        self.cmd_tab_scrollbar.bind('<ButtonPress-1>', self._on_scrollbar_click)
        self.cmd_tab_scrollbar.bind('<B1-Motion>', self._on_scrollbar_drag)
        self._scrollbar_drag_start = None
        self._scrollbar_pos = (0, 1)
        self.cmd_tab_canvas.configure(xscrollcommand=self._on_cmd_tab_scroll)
        
        # 绑定调整大小事件
        self.cmd_tab_frame.bind('<Configure>', self._on_cmd_tab_configure)
        self.cmd_tab_canvas.bind('<Configure>', self._on_cmd_canvas_configure)
        
        # 指令窗口数据
        self.cmd_windows = {}  # {window_id: {'frame': frame, 'text': ModernScrolledText}}
        self.current_cmd_window = 0
        self.cmd_window_counter = 0
        self.cmd_tab_buttons = {}  # {window_id: NavButton}
        
        # 指令显示区容器 - 必须在创建窗口之前定义
        self.cmd_display_container = tk.Frame(inner, bg=COLOR_BG_SECONDARY)
        self.cmd_display_container.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.cmd_display_container.rowconfigure(0, weight=1)
        self.cmd_display_container.columnconfigure(0, weight=1)
        
        # 创建第一个主窗口
        self._create_cmd_window(is_main=True)
        
        # 兼容旧代码：game_area 指向当前窗口
        self.game_area = self.cmd_windows[0]['text']
        
        # 命令历史记录
        self.cmd_history = []
        self.cmd_history_index = -1
        
        # 指令输入框
        cmd_input_frame = tk.Frame(inner, bg=COLOR_BG_SECONDARY)
        cmd_input_frame.grid(row=2, column=0, sticky='ew', padx=10, pady=(5, 10))
        cmd_input_frame.columnconfigure(0, weight=1)
        
        self.cmd_entry = ModernEntry(cmd_input_frame, font=FONT_GAME)
        self.cmd_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        self.cmd_entry.bind('<Return>', lambda e: self._send_command())
        self.cmd_entry.bind('<Up>', self._on_cmd_history_up)
        self.cmd_entry.bind('<Down>', self._on_cmd_history_down)
        
        exec_btn = ModernButton(
            cmd_input_frame, text="执行", accent=True,
            width=100, height=48, font=FONT_BUTTON,
            command=self._send_command
        )
        exec_btn.grid(row=0, column=1)
    
    def _on_cmd_history_up(self, event):
        """按上键显示上一条历史命令"""
        if not self.cmd_history:
            return 'break'
        
        if self.cmd_history_index == -1:
            # 保存当前输入
            self.cmd_history_temp = self.cmd_entry.get()
            self.cmd_history_index = len(self.cmd_history) - 1
        elif self.cmd_history_index > 0:
            self.cmd_history_index -= 1
        
        self.cmd_entry.delete(0, 'end')
        self.cmd_entry.insert(0, self.cmd_history[self.cmd_history_index])
        return 'break'
    
    def _on_cmd_history_down(self, event):
        """按下键显示下一条历史命令"""
        if self.cmd_history_index == -1:
            return 'break'
        
        if self.cmd_history_index < len(self.cmd_history) - 1:
            self.cmd_history_index += 1
            self.cmd_entry.delete(0, 'end')
            self.cmd_entry.insert(0, self.cmd_history[self.cmd_history_index])
        else:
            # 恢复原来的输入
            self.cmd_history_index = -1
            self.cmd_entry.delete(0, 'end')
            self.cmd_entry.insert(0, self.cmd_history_temp)
        return 'break'
    
    def _create_cmd_window(self, is_main=False):
        """创建新的指令窗口"""
        from .config import FONT_GAME, FONT_BUTTON
        
        window_id = self.cmd_window_counter
        self.cmd_window_counter += 1
        
        # 创建标签按钮（使用NavButton风格）
        tab_name = "主窗口" if is_main else f"窗口{window_id}"
        
        # 创建标签容器（包含按钮和关闭按钮）
        tab_container = tk.Frame(self.cmd_tab_frame, bg=COLOR_BG_SECONDARY)
        tab_container.pack(side='left', padx=3)
        
        # 使用NavButton
        tab_btn = NavButton(
            tab_container, text=tab_name, width=120, height=52,
            font=FONT_BUTTON, selected=(window_id == self.current_cmd_window),
            command=lambda wid=window_id: self._switch_cmd_window(wid)
        )
        tab_btn.pack(side='left')
        
        # 非主窗口添加关闭按钮
        close_btn = None
        if not is_main:
            close_btn = tk.Label(tab_container, text='×', font=(UI_FONT, 14),
                                bg=COLOR_BG_SECONDARY, fg=COLOR_FG_TERTIARY, cursor='hand2')
            close_btn.pack(side='left', padx=(2, 0))
            close_btn.bind('<Button-1>', lambda e, wid=window_id: self._close_cmd_window(wid))
            close_btn.bind('<Enter>', lambda e, btn=close_btn: btn.config(fg='#FF6666'))
            close_btn.bind('<Leave>', lambda e, btn=close_btn: btn.config(fg=COLOR_FG_TERTIARY))
        
        # 创建内容区域
        content_frame = tk.Frame(self.cmd_display_container, bg=COLOR_BG_PRIMARY)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)
        
        text_widget = ModernScrolledText(
            content_frame, font=FONT_GAME, width=30,
            bg=COLOR_BG_PRIMARY, fg=COLOR_FG_PRIMARY
        )
        text_widget.grid(row=0, column=0, sticky='nsew')
        
        self.cmd_windows[window_id] = {
            'frame': content_frame,
            'text': text_widget,
            'tab_container': tab_container,
            'tab_btn': tab_btn,
            'close_btn': close_btn,
            'is_main': is_main
        }
        self.cmd_tab_buttons[window_id] = tab_btn
        
        # 切换到新窗口
        self._switch_cmd_window(window_id)
        
        return window_id
    
    def _switch_cmd_window(self, window_id):
        """切换指令窗口"""
        if window_id not in self.cmd_windows:
            return
        
        # 取消选中当前窗口
        if self.current_cmd_window in self.cmd_windows:
            self.cmd_windows[self.current_cmd_window]['frame'].grid_forget()
            self.cmd_windows[self.current_cmd_window]['tab_btn'].set_selected(False)
        
        # 选中新窗口
        self.current_cmd_window = window_id
        self.cmd_windows[window_id]['frame'].grid(row=0, column=0, sticky='nsew')
        self.cmd_windows[window_id]['tab_btn'].set_selected(True)
    
    def _close_cmd_window(self, window_id):
        """关闭指令窗口"""
        if window_id not in self.cmd_windows:
            return
        
        # 不能关闭主窗口
        if self.cmd_windows[window_id].get('is_main'):
            return
        
        # 销毁组件
        self.cmd_windows[window_id]['frame'].destroy()
        self.cmd_windows[window_id]['tab_container'].destroy()
        
        del self.cmd_windows[window_id]
        del self.cmd_tab_buttons[window_id]
        
        # 如果关闭的是当前窗口，切换到主窗口
        if self.current_cmd_window == window_id:
            self._switch_cmd_window(0)
    
    def _on_cmd_tab_scroll(self, *args):
        """标签滚动回调"""
        self._scrollbar_pos = (float(args[0]), float(args[1]))
        self._draw_scrollbar_thumb()
        # 检查是否需要显示滚动条
        if float(args[0]) > 0 or float(args[1]) < 1:
            self.cmd_tab_scrollbar_frame.pack(side='bottom', fill='x')
        else:
            self.cmd_tab_scrollbar_frame.pack_forget()
    
    def _draw_scrollbar_thumb(self):
        """绘制水平滚动条滑块"""
        self.cmd_tab_scrollbar.delete('thumb')
        w = self.cmd_tab_scrollbar.winfo_width()
        if w < 10:
            return
        
        lo, hi = self._scrollbar_pos
        if hi - lo >= 1:
            return
        
        x1 = int(lo * w) + 2
        x2 = int(hi * w) - 2
        if x2 - x1 < 20:
            x2 = x1 + 20
        
        # 绘制圆角滑块
        self.cmd_tab_scrollbar.create_rectangle(x1, 2, x2, 6, fill=COLOR_FG_TERTIARY, 
                                                  outline='', tags='thumb')
    
    def _on_scrollbar_click(self, event):
        """滚动条点击"""
        w = self.cmd_tab_scrollbar.winfo_width()
        if w < 10:
            return
        ratio = event.x / w
        self.cmd_tab_canvas.xview_moveto(ratio)
        self._scrollbar_drag_start = event.x
    
    def _on_scrollbar_drag(self, event):
        """滚动条拖动"""
        if self._scrollbar_drag_start is None:
            return
        w = self.cmd_tab_scrollbar.winfo_width()
        if w < 10:
            return
        delta = (event.x - self._scrollbar_drag_start) / w
        new_pos = self._scrollbar_pos[0] + delta
        self.cmd_tab_canvas.xview_moveto(new_pos)
        self._scrollbar_drag_start = event.x
    
    def _on_cmd_tab_configure(self, event):
        """标签内容大小变化"""
        self.cmd_tab_canvas.configure(scrollregion=self.cmd_tab_canvas.bbox('all'))
        self._draw_scrollbar_thumb()
    
    def _on_cmd_canvas_configure(self, event):
        """标签画布大小变化"""
        self._draw_scrollbar_thumb()
    
    def _setup_info_panel(self, parent):
        from .config import FONT_MAP, FONT_STATUS
        
        right_frame = tk.Frame(parent, bg=COLOR_BG_PRIMARY)
        right_frame.grid(row=0, column=2, sticky='nsew', padx=(5, 0))
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        # 上半部分圆角卡片：头像/牌桌
        top_card = RoundedFrame(right_frame, radius=RADIUS_MEDIUM)
        top_card.grid(row=0, column=0, sticky='nsew', pady=(0, 5))
        
        top_inner = top_card.inner
        top_inner.rowconfigure(0, weight=1)
        top_inner.columnconfigure(0, weight=1)
        
        # 视图容器（用于切换大头像和牌桌）
        self.view_container = tk.Frame(top_inner, bg=COLOR_BG_SECONDARY)
        self.view_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.view_container.rowconfigure(0, weight=1)
        self.view_container.columnconfigure(0, weight=1)
        
        # 大头像视图（默认显示）
        self.avatar_view = tk.Frame(self.view_container, bg=COLOR_BG_SECONDARY)
        self.avatar_view.grid(row=0, column=0, sticky='nsew')
        
        # 大头像显示（128x128）- 简化布局，直接用Frame包裹
        avatar_frame = tk.Frame(self.avatar_view, bg=COLOR_BG_TERTIARY, 
                                padx=10, pady=10)
        
        self.avatar_display = AvatarDisplay(
            avatar_frame, size=128, 
            bg=COLOR_BG_TERTIARY,
            highlightthickness=0
        )
        self.avatar_display.pack()
        
        # 使用place实现居中，绑定到avatar_view的Configure事件
        self._avatar_frame = avatar_frame  # 保存引用
        
        def center_avatar(event=None):
            self.avatar_view.update_idletasks()
            view_w = self.avatar_view.winfo_width()
            view_h = self.avatar_view.winfo_height()
            frame_w = self._avatar_frame.winfo_reqwidth()
            frame_h = self._avatar_frame.winfo_reqheight()
            if view_w > 1 and view_h > 1:
                x = (view_w - frame_w) // 2
                y = (view_h - frame_h) // 2
                self._avatar_frame.place(x=x, y=y)
        
        self.avatar_view.bind('<Configure>', center_avatar)
        # 初始居中
        self.avatar_view.after(100, center_avatar)
        
        # 麻将牌桌视图（默认隐藏）
        self.table_view = MahjongTableView(self.view_container)
        # 初始不显示牌桌
        
        # 当前视图模式
        self.current_view_mode = 'avatar'  # 'avatar' 或 'table'
        
        # 地图文本（隐藏，保留兼容性）
        self.map_text = tk.Text(
            top_inner, font=FONT_MAP, width=24, height=1,
            bg=COLOR_BG_PRIMARY, fg=COLOR_FG_PRIMARY,
            relief='flat', bd=0, padx=10, pady=0,
            state='disabled'
        )
        # 不再显示地图文本
        # self.map_text.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))
        
        # 下半部分圆角卡片：状态
        bottom_card = RoundedFrame(right_frame, radius=RADIUS_MEDIUM)
        bottom_card.grid(row=1, column=0, sticky='nsew', pady=(5, 0))
        
        bottom_inner = bottom_card.inner
        bottom_inner.rowconfigure(0, weight=1)
        bottom_inner.columnconfigure(0, weight=1)
        
        self.status_text = tk.Text(
            bottom_inner, font=FONT_STATUS, width=24, height=10,
            bg=COLOR_BG_PRIMARY, fg=COLOR_FG_PRIMARY,
            relief='flat', bd=0, padx=12, pady=10,
            state='disabled'
        )
        self.status_text.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    
    def _switch_channel(self, channel_id):
        if channel_id != self.current_channel:
            self.current_channel = channel_id
            self._update_channel_buttons()
            self._update_online_display()
            self.on_switch_channel(channel_id)
            self.chat_area.config(state='normal')
            self.chat_area.delete('1.0', 'end')
            self.chat_area.config(state='disabled')
    
    def _update_channel_buttons(self):
        """更新频道按钮状态（NavButton）"""
        for ch_id, btn in self.channel_buttons.items():
            btn.set_selected(ch_id == self.current_channel)
    
    def _update_online_display(self):
        self.online_text.config(state='normal')
        self.online_text.delete('1.0', 'end')
        
        if not self.online_users:
            self.online_text.insert('end', "在线: -", 'prefix')
            self.online_text.config(state='disabled')
            return
        
        self.online_text.insert('end', "在线: ", 'prefix')
        
        # 分离当前频道和其他频道的用户
        first = True
        for user in self.online_users:
            name = user.get('name', '???')
            user_channel = user.get('channel', 1)
            
            if not first:
                self.online_text.insert('end', " ", 'prefix')
            first = False
            
            if user_channel == self.current_channel:
                self.online_text.insert('end', name, 'bold')
            else:
                self.online_text.insert('end', name, 'dim')
        
        self.online_text.config(state='disabled')
    
    def _send_chat(self):
        text = self.chat_entry.get().strip()
        if text:
            self.on_chat(text, self.current_channel)
            self.chat_entry.delete(0, 'end')
    
    def _send_command(self):
        text = self.cmd_entry.get().strip()
        if text:
            # 保存到历史记录
            if text and (not self.cmd_history or self.cmd_history[-1] != text):
                self.cmd_history.append(text)
                # 限制历史记录数量
                if len(self.cmd_history) > 100:
                    self.cmd_history.pop(0)
            self.cmd_history_index = -1
            
            self.on_command(text)
            self.cmd_entry.delete(0, 'end')
            # 需要打牌时用 /d，否则用 /
            # 但如果刚输入的是特殊命令（如 /exit），保持 / 前缀
            if self.logged_in:
                special_cmds = ['/exit', '/quit', '/back', '/y', '/n']
                if self.need_discard and not any(text.lower().startswith(c) for c in special_cmds):
                    self.cmd_entry.insert(0, '/d ')
                else:
                    self.cmd_entry.insert(0, '/')
    
    def set_logged_in(self):
        """登录成功后调用"""
        self.logged_in = True
        self.cmd_entry.delete(0, 'end')
        self.cmd_entry.insert(0, '/')
    
    def set_mahjong_mode(self, enabled):
        """设置麻将游戏模式（用于退出确认判断）"""
        self.in_mahjong_game = enabled
    
    def set_cmd_prefix(self, prefix):
        """设置命令输入框的前缀
        
        Args:
            prefix: '/d ' 打牌模式, '/' 操作模式
        """
        self.cmd_entry.delete(0, 'end')
        self.cmd_entry.insert(0, prefix)
    
    def update_online_users(self, users):
        self.online_users = users
        self._update_online_display()
    
    def add_system_message(self, text):
        self.chat_area.config(state='normal')
        self.chat_area.insert('end', f"[SYS] {text}\n", 'system')
        self.chat_area.config(state='disabled')
        self.chat_area.see('end')
    
    def add_chat_message(self, name, text, channel=1, time_str=''):
        if channel == self.current_channel:
            self.chat_area.config(state='normal')
            # 时间用小灰色字体显示，格式：[HH:MM] 名字: 消息
            if time_str:
                self.chat_area.insert('end', f"[{time_str}] ", 'time')
            self.chat_area.insert('end', f"{name}: ", 'name')
            self.chat_area.insert('end', f"{text}\n", 'chat')
            self.chat_area.config(state='disabled')
            self.chat_area.see('end')
    
    def show_chat_history(self, messages, channel):
        """显示聊天历史，滚动到最后一条'上线了'消息"""
        if channel != self.current_channel:
            return
        
        self.chat_area.config(state='normal')
        self.chat_area.delete('1.0', 'end')
        
        last_online_line = None
        line_num = 1
        
        for m in messages:
            name = m.get('name', '???')
            text = m.get('text', '')
            self.chat_area.insert('end', f"{name}: {text}\n", 'chat')
            
            # 找最后一条"上线了"消息
            if '上线了' in text:
                last_online_line = line_num
            line_num += 1
        
        self.chat_area.config(state='disabled')
        
        # 滚动到最后一条"上线了"消息
        if last_online_line:
            self.chat_area.see(f'{last_online_line}.0')
        else:
            self.chat_area.see('end')
    
    def add_game_message(self, text, to_main=True, update_last=False):
        """添加游戏消息
        
        Args:
            text: 消息内容
            to_main: 是否发送到主窗口，False则发到当前窗口
            update_last: 是否更新最后一行而不是新增
        """
        # 确定目标窗口
        if to_main:
            target_window = 0
        else:
            target_window = self.current_cmd_window
        
        if target_window in self.cmd_windows:
            text_widget = self.cmd_windows[target_window]['text']
            text_widget.config(state='normal')
            if update_last:
                # 删除最后一行并替换
                text_widget.delete('end-2l', 'end-1l')
            text_widget.insert('end', f"{text}\n")
            text_widget.config(state='disabled')
            text_widget.see('end')
        else:
            # 兼容：如果没有多窗口系统，使用旧的game_area
            self.game_area.config(state='normal')
            if update_last:
                self.game_area.delete('end-2l', 'end-1l')
            self.game_area.insert('end', f"{text}\n")
            self.game_area.config(state='disabled')
            self.game_area.see('end')
    
    def clear_game_area(self):
        """清空当前窗口"""
        if self.current_cmd_window in self.cmd_windows:
            text_widget = self.cmd_windows[self.current_cmd_window]['text']
            text_widget.config(state='normal')
            text_widget.delete('1.0', 'end')
            text_widget.config(state='disabled')
        else:
            self.game_area.config(state='normal')
            self.game_area.delete('1.0', 'end')
            self.game_area.config(state='disabled')
    
    def update_map(self, map_lines):
        self.map_text.config(state='normal')
        self.map_text.delete('1.0', 'end')
        if map_lines:
            for line in map_lines:
                self.map_text.insert('end', line + '\n')
        else:
            self.map_text.insert('end', "等待数据...")
        self.map_text.config(state='disabled')
    
    def update_status(self, player_data):
        self._cached_player_data = player_data  # 缓存玩家数据
        
        # 如果有手牌，使用手牌显示模式
        if self.current_hand:
            self._refresh_status_with_hand()
            # 更新头像
            if player_data:
                avatar_data = player_data.get('avatar')
                if avatar_data:
                    self.avatar_display.set_avatar(avatar_data)
            return
        
        self.status_text.config(state='normal')
        self.status_text.delete('1.0', 'end')
        
        # 配置标签样式
        self.status_text.tag_config('info', foreground='#888888', font=(UI_FONT, 9))
        
        # 第一行显示位置指示器（灰色小号字体）
        location_path = self.get_location_path()
        self.status_text.insert('end', f"{location_path}\n", 'info')
        
        if player_data:
            p = player_data
            title = p.get('title') or '新人'
            accessory = p.get('accessory') or '无'
            status = f"""══════════════════
  {p.get('name', '???')}
══════════════════
【{title}】

Lv.{p.get('level', 1)}
金币: {p.get('gold', 0)}G
饰品: {accessory}
══════════════════
"""
            # 更新头像
            avatar_data = p.get('avatar')
            if avatar_data:
                self.avatar_display.set_avatar(avatar_data)
        else:
            status = "等待中..."
        self.status_text.insert('end', status)
        
        self.status_text.config(state='disabled')
    
    def switch_to_avatar_view(self):
        """切换到大头像视图"""
        if self.current_view_mode == 'avatar':
            return
        self.current_view_mode = 'avatar'
        self.table_view.grid_forget()
        self.avatar_view.grid(row=0, column=0, sticky='nsew')
        # 刷新状态显示（恢复头像和个人信息）
        if self._cached_player_data:
            self.update_status(self._cached_player_data)
    
    def switch_to_table_view(self):
        """切换到牌桌视图"""
        if self.current_view_mode == 'table':
            return
        self.current_view_mode = 'table'
        self.avatar_view.grid_forget()
        self.table_view.grid(row=0, column=0, sticky='nsew')
    
    def update_table(self, room_data):
        """更新牌桌显示"""
        if room_data:
            self._cached_room_data = room_data  # 缓存用于状态窗口
            self.switch_to_table_view()
            self.table_view.update_table(room_data)
            self._refresh_status_with_hand()  # 刷新状态窗口
        else:
            self._cached_room_data = None
            self.switch_to_avatar_view()
    
    def show_game_invite(self, invite_data):
        """显示游戏邀请通知"""
        from_player = invite_data.get('from', '???')
        game = invite_data.get('game', '???')
        message = invite_data.get('message', f'{from_player} 邀请你玩 {game}')
        
        # 在聊天区和游戏区都显示邀请
        self.add_system_message(f"🎮 {message}")
        self.add_game_message(f"\n{message}\n")
    
    def update_hand(self, hand_tiles, drawn_tile=None, tenpai_analysis=None, need_discard=False):
        """更新手牌显示（在右下角状态窗口）
        
        Args:
            hand_tiles: 手牌列表
            drawn_tile: 新摸的牌（显示在右侧并高亮）
            tenpai_analysis: 听牌分析数据
            need_discard: 是否需要出牌（吃碰后）
        """
        self.current_hand = hand_tiles
        self.drawn_tile = drawn_tile
        self.tenpai_analysis = tenpai_analysis
        self._refresh_status_with_hand()
        
        # 如果有新摸的牌或服务器指定需要出牌
        if drawn_tile or need_discard:
            self.need_discard = True
            self.set_cmd_prefix('/d ')
    
    def _get_tile_color(self, tile):
        """根据牌的类型返回颜色"""
        if '万' in tile:
            return '#FF6B6B'  # 万子 - 红色
        elif '条' in tile:
            return '#7ED321'  # 条子 - 绿色
        elif '筒' in tile:
            return '#5DADE2'  # 筒子 - 蓝色
        elif tile in ['东', '南', '西', '北']:
            return '#F7DC6F'  # 风牌 - 黄色
        elif tile in ['中', '发', '白']:
            return '#BB8FCE'  # 三元牌 - 紫色
        else:
            return COLOR_FG_PRIMARY  # 默认色
    
    def _insert_colored_tile(self, tile, suffix='', bold=False):
        """插入带颜色的牌"""
        color = self._get_tile_color(tile)
        tag_name = f'tile_{color}'
        font = (UI_FONT, 10, 'bold') if bold else (UI_FONT, 10)
        self.status_text.tag_config(tag_name, foreground=color, font=font)
        self.status_text.insert('end', tile, tag_name)
        if suffix:
            self.status_text.insert('end', suffix)
    
    def _refresh_status_with_hand(self):
        """刷新状态显示（包含手牌）- 纵向列表"""
        self.status_text.config(state='normal')
        self.status_text.delete('1.0', 'end')
        
        # 配置标签样式
        self.status_text.tag_config('normal', foreground=COLOR_FG_PRIMARY)
        self.status_text.tag_config('drawn', foreground=COLOR_ACCENT, font=(UI_FONT, 10, 'bold'))
        self.status_text.tag_config('number', foreground=COLOR_FG_TERTIARY)
        self.status_text.tag_config('tile', foreground=COLOR_FG_PRIMARY, font=(UI_FONT, 10))
        self.status_text.tag_config('separator', foreground=COLOR_BORDER)
        self.status_text.tag_config('info', foreground='#888888', font=(UI_FONT, 9))
        self.status_text.tag_config('dora', foreground='#FFD700', font=(UI_FONT, 9, 'bold'))
        self.status_text.tag_config('tenpai', foreground='#00FF00', font=(UI_FONT, 9, 'bold'))
        self.status_text.tag_config('tenpai_hint', foreground='#90EE90', font=(UI_FONT, 9))
        self.status_text.tag_config('warning', foreground='#FF6B6B', font=(UI_FONT, 9))
        
        # 第一行显示位置指示器（灰色小号字体）
        location_path = self.get_location_path()
        self.status_text.insert('end', f"{location_path}\n", 'info')
        
        # 显示游戏状态信息（场风、宝牌等）
        if self._cached_room_data:
            rd = self._cached_room_data
            if rd.get('state') == 'playing':
                round_wind = rd.get('round_wind', '东')
                round_number = rd.get('round_number', 0)
                honba = rd.get('honba', 0)
                riichi_sticks = rd.get('riichi_sticks', 0)
                
                # round_number是0-3，显示时+1变成1-4局
                self.status_text.insert('end', f"{round_wind}{round_number + 1}局 {honba}本场", 'info')
                if riichi_sticks > 0:
                    self.status_text.insert('end', f" 立直{riichi_sticks}", 'info')
                self.status_text.insert('end', "\n", 'info')
                
                # 宝牌
                dora_tiles = rd.get('dora_tiles', [])
                if dora_tiles:
                    self.status_text.insert('end', "宝牌: ", 'info')
                    self.status_text.insert('end', " ".join([f"[{t}]" for t in dora_tiles]) + "\n", 'dora')
                
                self.status_text.insert('end', "──────────────\n", 'separator')
        
        # 手牌显示
        if self.current_hand:
            hand = self.current_hand
            drawn = self.drawn_tile
            
            self.status_text.insert('end', f"══ 手牌 ({len(hand)}张) ══\n", 'normal')
            
            # 如果当前听牌（13张时）
            if self.tenpai_analysis and self.tenpai_analysis.get('is_tenpai'):
                waiting = self.tenpai_analysis.get('waiting', [])
                waiting_count = self.tenpai_analysis.get('waiting_count', 0)
                has_yaku = self.tenpai_analysis.get('has_yaku', False)
                
                self.status_text.insert('end', f"🎯 听牌({waiting_count}张): ", 'tenpai')
                # waiting 可能是 [(牌名, 剩余数), ...] 或 [[牌名, 剩余数], ...] 格式
                waiting_strs = []
                for item in waiting:
                    if isinstance(item, (tuple, list)) and len(item) == 2:
                        tile_name, count = item
                        waiting_strs.append(f"{tile_name}×{count}")
                    elif isinstance(item, str):
                        waiting_strs.append(item)
                self.status_text.insert('end', " ".join(waiting_strs) + "\n", 'tenpai')
                
                # 显示是否有役
                if has_yaku:
                    self.status_text.insert('end', "✓ 有役\n", 'tenpai')
                else:
                    self.status_text.insert('end', "✗ 无役（需立直或凑役）\n", 'warning')
            
            self.status_text.insert('end', "──────────────\n", 'separator')
            
            # 检查是否立直中（立直后不显示向听提示）
            is_riichi = self._is_my_riichi()
            
            # 获取打出后可听牌的信息（立直后不需要）
            discard_to_tenpai = {}
            discard_has_yaku = {}
            if not is_riichi and self.tenpai_analysis:
                discard_to_tenpai = self.tenpai_analysis.get('discard_to_tenpai', {})
                discard_has_yaku = self.tenpai_analysis.get('discard_has_yaku', {})
            
            # 纵向列表显示，每行一张牌
            for i, tile in enumerate(hand):
                num = i + 1
                # 检查是否是新摸的牌（最后一张且有drawn标记）
                is_new = drawn and (i == len(hand) - 1) and (tile == drawn)
                
                # 检查打出这张牌后是否能听牌（立直后不显示）
                can_tenpai = tile in discard_to_tenpai
                tile_has_yaku = discard_has_yaku.get(tile, False)
                
                self.status_text.insert('end', f" {num:2d}. ", 'number')
                
                if is_new:
                    self._insert_colored_tile(tile, bold=True)
                    self.status_text.insert('end', " ★新", 'drawn')
                    if can_tenpai:
                        waiting = discard_to_tenpai[tile]
                        # waiting 可能是 [(牌名, 剩余数), ...] 或 [(牌名, 剩余数, 有役), ...] 格式
                        total = sum(item[1] for item in waiting if isinstance(item, (tuple, list)) and len(item) >= 2) if waiting else 0
                        yaku_hint = "" if tile_has_yaku else "(无役)"
                        self.status_text.insert('end', f" →听{len(waiting)}种{total}张{yaku_hint}\n", 'tenpai_hint' if tile_has_yaku else 'warning')
                    else:
                        self.status_text.insert('end', "\n")
                else:
                    self._insert_colored_tile(tile)
                    if can_tenpai:
                        waiting = discard_to_tenpai[tile]
                        total = sum(item[1] for item in waiting if isinstance(item, (tuple, list)) and len(item) >= 2) if waiting else 0
                        yaku_hint = "" if tile_has_yaku else "(无役)"
                        self.status_text.insert('end', f" →听{len(waiting)}种{total}张{yaku_hint}\n", 'tenpai_hint' if tile_has_yaku else 'warning')
                    else:
                        self.status_text.insert('end', "\n")
            
            self.status_text.insert('end', "──────────────\n", 'separator')
            self.status_text.insert('end', "输入 /d 编号\n", 'number')
            
            # 如果有可以听牌的选项，显示详细信息
            if discard_to_tenpai:
                self.status_text.insert('end', "──────────────\n", 'separator')
                self.status_text.insert('end', "【向听提示】\n", 'tenpai')
                for discard_tile, waiting_tiles in discard_to_tenpai.items():
                    tile_has_yaku = discard_has_yaku.get(discard_tile, False)
                    self.status_text.insert('end', f"打", 'info')
                    self._insert_colored_tile(discard_tile)
                    yaku_mark = "" if tile_has_yaku else " ✗无役"
                    self.status_text.insert('end', f":{yaku_mark} ", 'info' if tile_has_yaku else 'warning')
                    # waiting_tiles 可能是 [(牌名, 剩余数), ...] 或 [(牌名, 剩余数, 有役), ...] 格式
                    waiting_strs = []
                    for item in waiting_tiles:
                        if isinstance(item, (tuple, list)) and len(item) >= 2:
                            tile_name = item[0]
                            count = item[1]
                            waiting_strs.append(f"{tile_name}×{count}")
                        elif isinstance(item, str):
                            waiting_strs.append(item)
                    if waiting_strs:
                        self.status_text.insert('end', f"{' '.join(waiting_strs)}\n", 'tenpai_hint')
                    else:
                        self.status_text.insert('end', "(无)\n", 'info')
        else:
            # 没有手牌时显示玩家信息（与update_status格式一致）
            if self._cached_player_data:
                p = self._cached_player_data
                title = p.get('title') or '新人'
                accessory = p.get('accessory') or '无'
                status = f"""══════════════════
  {p.get('name', '???')}
══════════════════
【{title}】

Lv.{p.get('level', 1)}
金币: {p.get('gold', 0)}G
饰品: {accessory}
══════════════════
"""
                self.status_text.insert('end', status, 'normal')
        
        self.status_text.config(state='disabled')
    
    def show_action_prompt(self, actions, tile, from_player):
        """显示吃碰杠胡操作提示（在游戏区域显示）"""
        if not actions:
            return
        
        # 在游戏消息区显示操作提示
        prompt_lines = [f"\n{'='*20}", f"🀄 {from_player} 打出 [{tile}]", "可执行操作:"]
        
        action_cmds = []
        # 和牌优先显示
        if 'win' in actions:
            prompt_lines.append(f"  和 - 输入 /hu")
            action_cmds.append('/hu')
        if 'pong' in actions:
            prompt_lines.append(f"  碰 - 输入 /pong")
            action_cmds.append('/pong')
        if 'kong' in actions:
            prompt_lines.append(f"  杠 - 输入 /kong")
            action_cmds.append('/kong')
        if 'chow' in actions:
            chow_data = actions['chow']
            options = chow_data.get('options', [])
            if len(options) == 1:
                prompt_lines.append(f"  吃 - 输入 /chow")
                action_cmds.append('/chow')
            else:
                for idx, opt in enumerate(options):
                    prompt_lines.append(f"  吃{idx+1}: {' '.join(opt)} - 输入 /chow {idx+1}")
                    action_cmds.append(f'/chow {idx+1}')
        
        prompt_lines.append(f"  过 - 输入 /pass")
        prompt_lines.append(f"{'='*20}\n")
        
        for line in prompt_lines:
            self.add_game_message(line)
        
        # 等待操作时不需要打牌
        self.need_discard = False
        self.set_cmd_prefix('/')
    
    def show_self_action_prompt(self, actions):
        """显示立直/暗杠/加杠/自摸操作提示（在游戏区域显示）"""
        if not actions:
            return
        
        # 在游戏消息区显示操作提示
        prompt_lines = [f"\n{'='*20}", "🀄 可执行特殊操作:"]
        
        # 自摸优先显示
        if 'tsumo' in actions:
            prompt_lines.append(f"  自摸 - 输入 /tsumo")
        
        # 立直
        if 'riichi' in actions:
            riichi_tiles = actions['riichi']
            if isinstance(riichi_tiles, list) and riichi_tiles:
                prompt_lines.append(f"  立直 - 输入 /riichi <编号>")
                # 显示可以立直打出的牌
                prompt_lines.append(f"    可立直切: {' '.join(riichi_tiles[:5])}{'...' if len(riichi_tiles) > 5 else ''}")
        
        # 暗杠
        if 'ankan' in actions:
            for k in actions['ankan']:
                tile = k.get('tile', '')
                prompt_lines.append(f"  暗杠 [{tile}] - 输入 /ankan")
        
        # 加杠
        if 'kakan' in actions:
            for k in actions['kakan']:
                tile = k.get('tile', '')
                prompt_lines.append(f"  加杠 [{tile}] - 输入 /kakan")
        
        prompt_lines.append(f"{'='*20}\n")
        
        for line in prompt_lines:
            self.add_game_message(line)
        
        # 设置输入框为/（操作模式）
        self.set_cmd_prefix('/')
    
    def clear_hand(self):
        """清空手牌显示"""
        self.current_hand = None
        self.drawn_tile = None
        self.need_discard = False
        # 恢复正常状态显示
        self.update_status(self._cached_player_data)
        # 强制设置输入框为/
        self.set_cmd_prefix('/')
    
    def set_location(self, location):
        """设置当前位置"""
        self.current_location = location
        # 根据位置设置麻将游戏状态
        self.in_mahjong_game = (location == 'mahjong_playing')
        # 如果离开麻将相关位置，清空手牌和牌桌
        if not location.startswith('mahjong'):
            self.clear_hand()
            self.update_table(None)
        elif location == 'mahjong':
            # 返回麻将大厅
            self.clear_hand()
            self.update_table(None)
        # 刷新状态显示
        self._refresh_location_display()
    
    def _refresh_location_display(self):
        """刷新位置显示（在状态栏底部显示）"""
        # 只在没有手牌时显示位置信息
        if not self.current_hand:
            self.update_status(self._cached_player_data)
    
    def get_location_path(self):
        """获取位置路径字符串"""
        hierarchy = {
            'lobby': None,
            'profile': 'lobby',
            'jrpg': 'lobby',
            'mahjong': 'lobby',
            'mahjong_room': 'mahjong',
            'mahjong_playing': 'mahjong_room'
        }
        
        path = []
        loc = self.current_location
        while loc:
            # 特殊处理：房间显示房间ID
            if loc == 'mahjong_room' and self.current_room_id:
                # 从 room_X_YYY 格式提取数字部分
                room_id = self.current_room_id
                if isinstance(room_id, str) and '_' in room_id:
                    # 取最后一个下划线后的部分
                    room_id = room_id.split('_')[-1]
                name = f"房间{room_id}"
            else:
                name = self.location_names.get(loc, loc)
            path.insert(0, name)
            loc = hierarchy.get(loc)
        
        return ' > '.join(path)
    
    def _is_my_riichi(self):
        """检查当前玩家是否已立直"""
        if not self._cached_room_data or not self._cached_player_data:
            return False
        
        my_name = self._cached_player_data.get('name')
        if not my_name:
            return False
        
        positions = self._cached_room_data.get('positions', [])
        for pos_data in positions:
            if pos_data.get('name') == my_name:
                return pos_data.get('is_riichi', False)
        
        return False
