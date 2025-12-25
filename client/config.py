"""
客户端配置
"""
import os
import ctypes
import tkinter as tk
from tkinter import font as tkfont


# 版本号（从 version.txt 读取，由 build_client.py 打包时生成）
def _get_client_version():
    """从 version.txt 读取版本号"""
    try:
        version_file = os.path.join(os.path.dirname(__file__), 'version.txt')
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except:
        pass
    return None

VERSION = _get_client_version()

# 自动更新配置
UPDATE_SERVER = "https://raw.githubusercontent.com/eroubisu/GameLobby-Client/main/client"  # 更新服务器地址
VERSION_FILE = "/version.json"  # 版本信息文件
DOWNLOAD_PATH = ""  # 下载路径

# 网络配置
PORT = 5555
DEFAULT_HOST = "8.130.103.89"

# UI 配置
WINDOW_TITLE = "游戏大厅"
WINDOW_SIZE = "1600x900"
WINDOW_MIN_SIZE = (1200, 700)

# ============ 屏幕信息和UI尺寸适配 ============
# 全局UI尺寸变量（初始化后设置）
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_DPI = 96
UI_SCALE = 1.0

# Win11 风格圆角半径（根据DPI缩放）- 更圆润
RADIUS_SMALL = 10      # 小圆角（滚动条、小元素）
RADIUS_MEDIUM = 20     # 中圆角（按钮、卡片）
RADIUS_LARGE = 28      # 大圆角（大卡片、对话框）
RADIUS_XLARGE = 36     # 超大圆角（模态框）

# UI元素间距
PADDING_SMALL = 6
PADDING_MEDIUM = 10
PADDING_LARGE = 14
PADDING_XLARGE = 20

def get_screen_info():
    """获取屏幕分辨率和DPI信息"""
    global SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_DPI, UI_SCALE
    global RADIUS_SMALL, RADIUS_MEDIUM, RADIUS_LARGE, RADIUS_XLARGE
    global PADDING_SMALL, PADDING_MEDIUM, PADDING_LARGE, PADDING_XLARGE
    
    try:
        # 获取屏幕尺寸
        user32 = ctypes.windll.user32
        SCREEN_WIDTH = user32.GetSystemMetrics(0)
        SCREEN_HEIGHT = user32.GetSystemMetrics(1)
        
        # 获取DPI
        try:
            # Windows 10+
            dpi = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            SCREEN_DPI = int(96 * dpi / 100)
        except:
            try:
                hdc = user32.GetDC(0)
                SCREEN_DPI = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                user32.ReleaseDC(0, hdc)
            except:
                SCREEN_DPI = 96
        
        # 计算UI缩放比例
        UI_SCALE = SCREEN_DPI / 96.0
        
        # Win11风格圆角 - 根据屏幕尺寸自适应
        # Win11在各种分辨率下都使用较大的圆角
        base_scale = max(0.9, min(1.3, min(SCREEN_WIDTH / 1600, SCREEN_HEIGHT / 900)))
        combined_scale = base_scale * UI_SCALE
        
        # Win11 风格圆角 - 显著更圆润
        RADIUS_SMALL = max(6, int(7 * combined_scale))       # 滚动条、小元素
        RADIUS_MEDIUM = max(10, int(12 * combined_scale))    # 按钮、卡片
        RADIUS_LARGE = max(14, int(16 * combined_scale))     # 大卡片、对话框
        RADIUS_XLARGE = max(18, int(20 * combined_scale))    # 模态框
        
        # 调整间距
        PADDING_SMALL = max(6, int(6 * combined_scale))
        PADDING_MEDIUM = max(10, int(10 * combined_scale))
        PADDING_LARGE = max(14, int(14 * combined_scale))
        PADDING_XLARGE = max(18, int(20 * combined_scale))
        
    except Exception as e:
        pass  # 使用默认值
    
    return SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_DPI, UI_SCALE

# ============ DPI 感知设置 ============
def enable_dpi_awareness():
    """启用 Windows DPI 感知，解决字体模糊问题"""
    try:
        # Windows 10 1607+ 推荐方式
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            # Windows 8.1+
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                # Windows Vista+
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    
    # 获取屏幕信息
    get_screen_info()

# ============ 字体配置 ============
# 字体优先级列表（优先使用微软雅黑）
FONT_FAMILIES = [
    'Microsoft YaHei UI',   # 微软雅黑 UI
    'Microsoft YaHei',      # 微软雅黑
    'Segoe UI',             # Windows 默认
    'SimHei',               # 黑体
    'Arial Unicode MS',
]

FONT_MONO_FAMILIES = [
    'Microsoft YaHei UI',   # 微软雅黑 UI（更统一）
    'Consolas',
    'Cascadia Mono',
    'Courier New',
]

def get_available_font(families, root=None):
    """获取系统中可用的第一个字体"""
    if root is None:
        root = tk.Tk()
        root.withdraw()
        created_root = True
    else:
        created_root = False
    
    available = tkfont.families()
    
    for family in families:
        if family in available:
            if created_root:
                root.destroy()
            return family
    
    if created_root:
        root.destroy()
    return families[-1]  # 返回最后一个作为默认

# 延迟初始化字体（需要在 Tk 初始化后调用）
FONT_UI_FAMILY = None
FONT_MONO_FAMILY = None

def init_fonts(root):
    """初始化字体配置（需要在 Tk() 之后调用）"""
    global FONT_UI_FAMILY, FONT_MONO_FAMILY
    global FONT_CHAT, FONT_GAME, FONT_MAP, FONT_STATUS, FONT_BUTTON, FONT_LABEL, FONT_TITLE
    
    FONT_UI_FAMILY = get_available_font(FONT_FAMILIES, root)
    FONT_MONO_FAMILY = get_available_font(FONT_MONO_FAMILIES, root)
    
    # 统一使用UI字体，避免混用导致的对齐问题
    FONT_CHAT = (FONT_UI_FAMILY, 10)
    FONT_GAME = (FONT_UI_FAMILY, 10)
    FONT_MAP = (FONT_UI_FAMILY, 10)
    FONT_STATUS = (FONT_UI_FAMILY, 10)
    FONT_BUTTON = (FONT_UI_FAMILY, 10)
    FONT_LABEL = (FONT_UI_FAMILY, 10)
    FONT_TITLE = (FONT_UI_FAMILY, 22, 'bold')
    
    return FONT_UI_FAMILY, FONT_MONO_FAMILY

# 临时默认值 - 统一使用微软雅黑
FONT_CHAT = ('Microsoft YaHei UI', 10)
FONT_GAME = ('Microsoft YaHei UI', 10)
FONT_MAP = ('Microsoft YaHei UI', 10)
FONT_STATUS = ('Microsoft YaHei UI', 10)
FONT_BUTTON = ('Microsoft YaHei UI', 10)
FONT_LABEL = ('Microsoft YaHei UI', 10)
FONT_TITLE = ('Microsoft YaHei UI', 22, 'bold')

# Win11 风格配色
# 背景色
COLOR_BG_PRIMARY = '#202020'      # 主背景（深灰黑）
COLOR_BG_SECONDARY = '#2d2d2d'    # 次级背景
COLOR_BG_TERTIARY = '#383838'     # 三级背景（卡片）
COLOR_BG_HOVER = '#404040'        # 悬停背景

# 前景色
COLOR_FG_PRIMARY = '#ffffff'      # 主文字
COLOR_FG_SECONDARY = '#b3b3b3'    # 次级文字
COLOR_FG_TERTIARY = '#808080'     # 三级文字

# 强调色（Win11 蓝）
COLOR_ACCENT = '#0078d4'          # 主强调色
COLOR_ACCENT_HOVER = '#1a86d9'    # 悬停强调
COLOR_ACCENT_LIGHT = '#60cdff'    # 浅强调色

# 边框色
COLOR_BORDER = '#454545'          # 边框
COLOR_BORDER_LIGHT = '#5a5a5a'    # 浅边框

# 功能色
COLOR_SUCCESS = '#6ccb5f'         # 成功/在线
COLOR_WARNING = '#fcb900'         # 警告
COLOR_ERROR = '#ff6b6b'           # 错误

# 旧配置兼容
COLOR_GAME_BG = COLOR_BG_PRIMARY
COLOR_GAME_FG = COLOR_FG_PRIMARY
COLOR_MAP_BG = COLOR_BG_SECONDARY
COLOR_MAP_FG = COLOR_FG_PRIMARY
COLOR_STATUS_BG = COLOR_BG_SECONDARY
COLOR_STATUS_FG = COLOR_FG_PRIMARY
COLOR_INPUT_BG = COLOR_BG_TERTIARY
