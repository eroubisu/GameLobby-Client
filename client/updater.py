"""
自动更新模块
"""

import os
import sys
import json
import urllib.request
import urllib.error
import tempfile
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
import ctypes

from .config import (
    VERSION, UPDATE_SERVER, VERSION_FILE, DOWNLOAD_PATH,
    COLOR_BG_PRIMARY, COLOR_BG_SECONDARY, COLOR_BG_TERTIARY,
    COLOR_FG_PRIMARY, COLOR_FG_SECONDARY, COLOR_FG_TERTIARY,
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_ERROR,
    RADIUS_MEDIUM, enable_dpi_awareness
)


def compare_versions(v1, v2):
    """比较版本号，v1 > v2 返回 1，v1 < v2 返回 -1，相等返回 0"""
    parts1 = [int(x) for x in v1.split('.')]
    parts2 = [int(x) for x in v2.split('.')]
    
    for i in range(max(len(parts1), len(parts2))):
        p1 = parts1[i] if i < len(parts1) else 0
        p2 = parts2[i] if i < len(parts2) else 0
        if p1 > p2:
            return 1
        elif p1 < p2:
            return -1
    return 0


def check_for_update():
    """
    检查是否有新版本
    返回: (has_update, latest_version, download_url, changelog)
    """
    # 如果没有版本号（开发环境），跳过更新检查
    if not VERSION:
        return False, None, None, None
    
    try:
        url = UPDATE_SERVER + VERSION_FILE
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            latest_version = data.get('version', VERSION)
            download_url = data.get('download_url', UPDATE_SERVER + DOWNLOAD_PATH)
            changelog = data.get('changelog', '')
            
            has_update = compare_versions(latest_version, VERSION) > 0
            return has_update, latest_version, download_url, changelog
    except Exception as e:
        print(f"检查更新失败: {e}")
        return False, VERSION, None, None


def download_update(url, progress_callback=None, cancel_check=None, target_dir=None):
    """
    下载更新文件（支持取消）
    返回: 下载的文件路径，失败或取消返回 None
    """
    try:
        # 从 URL 提取文件名
        filename = url.split('/')[-1]
        if not filename.endswith('.exe'):
            filename = 'game_update.exe'
        
        # 确定下载目录
        if target_dir is None:
            if getattr(sys, 'frozen', False):
                # 打包后，下载到 exe 所在目录
                target_dir = os.path.dirname(sys.executable)
            else:
                # 开发模式，下载到当前目录
                target_dir = os.getcwd()
        
        target_file = os.path.join(target_dir, filename)
        
        # 使用 urlopen 分块下载，支持取消
        req = urllib.request.urlopen(url, timeout=60)
        total_size = int(req.headers.get('Content-Length', 0))
        downloaded = 0
        block_size = 8192
        
        with open(target_file, 'wb') as f:
            while True:
                # 检查是否取消
                if cancel_check and cancel_check():
                    req.close()
                    if os.path.exists(target_file):
                        os.remove(target_file)
                    return None
                
                chunk = req.read(block_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                
                if progress_callback and total_size > 0:
                    progress = min(100, downloaded * 100 // total_size)
                    progress_callback(progress)
        
        req.close()
        return target_file
    except urllib.error.HTTPError as e:
        print(f"下载更新失败 (HTTP {e.code}): {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"下载更新失败 (网络错误): {e.reason}")
        return None
    except Exception as e:
        print(f"下载更新失败: {type(e).__name__}: {e}")
        return None


def apply_update(new_exe_path):
    """
    应用更新：提示用户手动启动新版本
    """
    if not os.path.exists(new_exe_path):
        return False
    
    # 返回文件路径，让调用者处理
    return new_exe_path


# GitHub 仓库链接
GITHUB_REPO_URL = "https://github.com/eroubisu/game"


class RoundedButton(tk.Canvas):
    """圆角按钮 - Canvas 实现"""
    
    def __init__(self, parent, text, command=None, 
                 bg=COLOR_BG_TERTIARY, fg=COLOR_FG_SECONDARY,
                 hover_bg=None, hover_fg=COLOR_FG_PRIMARY,
                 font=('Microsoft YaHei UI', 12),
                 width=180, height=44, radius=None, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=parent.cget('bg'), highlightthickness=0, **kwargs)
        
        self.text = text
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg or self._lighten(bg)
        self.hover_fg = hover_fg
        self.font = font
        self.w = width
        self.h = height
        self.r = radius if radius else max(12, RADIUS_MEDIUM)  # 使用 config 的圆角
        self._disabled = False
        self._current_bg = bg
        self._current_fg = fg
        
        self._draw()
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_click)
    
    def _lighten(self, color):
        if color.startswith('#') and len(color) == 7:
            r = min(255, int(color[1:3], 16) + 25)
            g = min(255, int(color[3:5], 16) + 25)
            b = min(255, int(color[5:7], 16) + 25)
            return f'#{r:02x}{g:02x}{b:02x}'
        return color
    
    def _draw(self):
        self.delete('all')
        w, h, r = self.w, self.h, self.r
        
        # 圆角矩形点
        points = [
            r, 0, w-r, 0, w, 0, w, r,
            w, h-r, w, h, w-r, h, r, h,
            0, h, 0, h-r, 0, r, 0, 0, r, 0
        ]
        self.create_polygon(points, smooth=True, fill=self._current_bg, outline='', tags='bg')
        self.create_text(w//2, h//2, text=self.text, fill=self._current_fg, font=self.font, tags='text')
    
    def _on_enter(self, event):
        if not self._disabled:
            self._current_bg = self.hover_bg
            self._current_fg = self.hover_fg
            self._draw()
            self.config(cursor='hand2')
    
    def _on_leave(self, event):
        if not self._disabled:
            self._current_bg = self.bg
            self._current_fg = self.fg
            self._draw()
            self.config(cursor='')
    
    def _on_click(self, event):
        if not self._disabled and self.command:
            self.command()
    
    def set_disabled(self, disabled):
        self._disabled = disabled
        if disabled:
            self._current_bg = COLOR_BG_TERTIARY
            self._current_fg = COLOR_FG_TERTIARY
        else:
            self._current_bg = self.bg
            self._current_fg = self.fg
        self._draw()
        self.config(cursor='' if disabled else 'hand2')
    
    def set_text(self, text):
        self.text = text
        self._draw()


class UpdateDialog(tk.Toplevel):
    """更新对话框（强制更新，关闭则退出程序）"""
    
    def __init__(self, parent, latest_version, changelog, download_url):
        super().__init__(parent)
        self.parent = parent
        self.title("发现新版本")
        self.configure(bg=COLOR_BG_PRIMARY)
        
        self.download_url = download_url
        self.latest_version = latest_version
        self.result = False
        self.is_downloading = False
        self.cancel_download = False
        
        # ========== DPI 感知 ==========
        enable_dpi_awareness()
        
        # ========== 固定字体大小（DPI已由系统处理）==========
        font_size_normal = 10
        font_size_small = 9
        font_size_large = 14
        font_size_title = 18
        
        # ========== 窗口大小 ==========
        width, height = 1000, 800
        
        # 居中显示
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(800, 600)
        self.resizable(True, True)
        
        # 拦截关闭按钮
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # ========== 主容器 ==========
        main_frame = tk.Frame(self, bg=COLOR_BG_PRIMARY)
        main_frame.pack(fill='both', expand=True, padx=35, pady=30)
        
        # ========== 标题区 ==========
        title_label = tk.Label(
            main_frame, 
            text=f"新版本 v{latest_version} 已发布",
            font=('Microsoft YaHei UI', font_size_title, 'bold'),
            bg=COLOR_BG_PRIMARY, fg=COLOR_ACCENT
        )
        title_label.pack(pady=(0, 12))
        
        version_label = tk.Label(
            main_frame, 
            text=f"当前版本: v{VERSION}",
            font=('Microsoft YaHei UI', font_size_normal),
            bg=COLOR_BG_PRIMARY, fg=COLOR_FG_TERTIARY
        )
        version_label.pack(pady=(0, 5))
        
        warn_label = tk.Label(
            main_frame, 
            text="请更新后再使用",
            font=('Microsoft YaHei UI', font_size_normal),
            bg=COLOR_BG_PRIMARY, fg=COLOR_ERROR
        )
        warn_label.pack(pady=(0, 20))
        
        # ========== 更新日志标题 ==========
        log_title = tk.Label(
            main_frame, 
            text="更新内容:",
            font=('Microsoft YaHei UI', font_size_large, 'bold'),
            bg=COLOR_BG_PRIMARY, fg=COLOR_FG_SECONDARY, anchor='w'
        )
        log_title.pack(fill='x', pady=(0, 8))
        
        # ========== 底部区域（先pack，确保始终显示）==========
        bottom_frame = tk.Frame(main_frame, bg=COLOR_BG_PRIMARY)
        bottom_frame.pack(side='bottom', fill='x')
        
        # 底部提示
        tip_label = tk.Label(
            bottom_frame, 
            text="也可以在 GitHub Releases 页面手动下载最新版本",
            font=('Microsoft YaHei UI', font_size_small),
            bg=COLOR_BG_PRIMARY, fg=COLOR_FG_TERTIARY
        )
        tip_label.pack(pady=(12, 0))
        
        # 按钮尺寸
        btn_width = 160
        btn_height = 50
        
        # 按钮区
        self.btn_frame = tk.Frame(bottom_frame, bg=COLOR_BG_PRIMARY)
        self.btn_frame.pack(pady=(20, 0))
        
        # GitHub 按钮（圆角）
        self.github_btn = RoundedButton(
            self.btn_frame, 
            text="访问仓库",
            command=self._open_github,
            bg=COLOR_BG_TERTIARY, fg=COLOR_FG_SECONDARY,
            font=('Microsoft YaHei UI', font_size_normal),
            width=btn_width, height=btn_height
        )
        self.github_btn.pack(side='left', padx=(0, 15))
        
        # 下载按钮（圆角）
        self.update_btn = RoundedButton(
            self.btn_frame, 
            text="立即更新",
            command=self._start_update,
            bg=COLOR_ACCENT, fg=COLOR_FG_PRIMARY,
            hover_bg=COLOR_ACCENT_HOVER,
            font=('Microsoft YaHei UI', font_size_normal, 'bold'),
            width=btn_width, height=btn_height
        )
        self.update_btn.pack(side='left', padx=(15, 0))
        
        # 进度条区域（初始隐藏）
        self.progress_frame = tk.Frame(bottom_frame, bg=COLOR_BG_PRIMARY)
        self.progress_label = tk.Label(
            self.progress_frame, text="准备下载...",
            font=('Microsoft YaHei UI', font_size_small),
            bg=COLOR_BG_PRIMARY, fg=COLOR_FG_SECONDARY
        )
        self.progress_bg = tk.Frame(self.progress_frame, bg='#404040', height=8)
        self.progress_bar = tk.Frame(self.progress_bg, bg=COLOR_ACCENT, height=8, width=0)
        
        # ========== 日志容器（填充剩余空间）==========
        log_container = tk.Frame(main_frame, bg=COLOR_BG_SECONDARY, bd=0)
        log_container.pack(fill='both', expand=True, pady=(0, 0))
        
        self.log_text = tk.Text(
            log_container, 
            font=('Microsoft YaHei UI', font_size_normal),
            bg=COLOR_BG_SECONDARY, fg='#e0e0e0',
            relief='flat', bd=0, padx=15, pady=12,
            wrap='word', spacing1=4, spacing3=4,
            highlightthickness=0
        )
        self.log_text.pack(fill='both', expand=True)
        
        changelog_display = changelog if changelog else "暂无更新说明"
        self.log_text.insert('1.0', changelog_display)
        self.log_text.config(state='disabled')
        
        # 确保窗口显示在最前
        self.transient(parent)  # 设置为父窗口的临时窗口
        self.attributes('-topmost', True)  # 置顶
        self.lift()
        self.focus_force()
        self.grab_set()  # 模态
        self.update_idletasks()
        # 稍后取消置顶（让其他窗口可以覆盖）
        self.after(100, lambda: self.attributes('-topmost', False))
    
    def _open_github(self):
        """打开 GitHub 仓库页面"""
        import webbrowser
        webbrowser.open(GITHUB_REPO_URL + "/releases")
    
    def _on_close(self):
        """关闭窗口时退出程序"""
        if self.is_downloading:
            # 询问是否取消下载
            if messagebox.askyesno("取消下载", "正在下载更新，确定要取消吗？\n\n取消后程序将退出。"):
                self.cancel_download = True
                self.is_downloading = False
                self.parent.destroy()
                sys.exit(0)
            return
        # 关闭更新窗口 = 退出程序
        self.parent.destroy()
        sys.exit(0)
    
    def _start_update(self):
        """开始更新"""
        if not self.download_url:
            messagebox.showerror("更新失败", "下载地址无效，请点击「访问 GitHub 仓库」按钮手动下载。")
            return
        
        self.is_downloading = True
        self.update_btn.set_disabled(True)
        
        # 显示进度区域 - 在按钮之前插入
        self.progress_frame.pack(fill='x', pady=(0, 15), before=self.btn_frame)
        self.progress_label.pack(anchor='w')
        self.progress_bg.pack(fill='x', pady=(5, 0))
        self.progress_bar.place(x=0, y=0, height=10, width=0)
        
        # 进度变量
        self._download_progress = 0
        self._download_result = None  # None=进行中, 文件路径=成功, False=失败
        
        # 定时更新UI的函数
        def poll_progress():
            if not self.winfo_exists():
                return
            
            # 检查是否完成
            if self._download_result is not None:
                if self._download_result:
                    # 下载成功
                    self._do_apply_update(self._download_result)
                else:
                    # 下载失败
                    self._do_download_failed()
                return
            
            if self.is_downloading:
                self.progress_label.config(text=f"下载进度: {self._download_progress}%")
                try:
                    bar_width = max(1, int(self.progress_bg.winfo_width() * self._download_progress / 100))
                    self.progress_bar.place(x=0, y=0, height=10, width=bar_width)
                except:
                    pass
                self.after(100, poll_progress)  # 每100ms更新一次
        
        # 启动UI轮询
        self.after(100, poll_progress)
        
        # 在线程中下载
        def download_thread():
            def update_progress(progress):
                self._download_progress = progress
            
            def check_cancel():
                return self.cancel_download
            
            temp_file = download_update(self.download_url, update_progress, check_cancel)
            
            if self.cancel_download:
                return  # 已取消，不做任何处理
            
            # 设置结果，让轮询函数处理
            self._download_result = temp_file if temp_file else False
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def _do_apply_update(self, downloaded_file):
        """应用更新"""
        self.is_downloading = False
        
        # 检查文件是否存在
        if not os.path.exists(downloaded_file):
            messagebox.showerror("更新失败", f"下载的文件不存在:\n{downloaded_file}")
            return
        
        # 显示完成信息
        file_size = os.path.getsize(downloaded_file)
        self.progress_label.config(text=f"下载完成! ({file_size / 1024 / 1024:.1f}MB)")
        self.update()
        
        # 弹窗提示并退出
        messagebox.showinfo("下载完成", f"新版本已下载:\n{downloaded_file}\n\n点击确定退出程序。")
        os._exit(0)
    
    def _do_download_failed(self):
        """下载失败"""
        self.is_downloading = False
        messagebox.showerror("更新失败", "下载更新文件失败，请检查网络后重试。\n\n您也可以点击「访问 GitHub 仓库」按钮手动下载。")
        self.update_btn.set_disabled(False)
        self.update_btn.set_text("重试")


def check_and_prompt_update(parent):
    """
    检查更新并在有新版本时弹出对话框（强制更新）
    返回: True 如果用户选择更新（程序将退出），False 无需更新继续运行
    """
    has_update, latest_version, download_url, changelog = check_for_update()
    
    if has_update and download_url:
        dialog = UpdateDialog(parent, latest_version, changelog, download_url)
        parent.wait_window(dialog)
        # 如果到这里说明对话框被关闭了，程序应该已经退出
        # 但以防万一，这里也退出
        sys.exit(0)
    
    return False
