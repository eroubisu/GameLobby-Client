"""
客户端打包脚本
运行此脚本将客户端打包为单个exe文件
输出: game_v版本号.exe
"""

import os
import sys
import subprocess
import shutil
import json

# ============ 版本配置（每次更新时修改这里） ============
VERSION = "1.1.11"                    # 客户端版本号
RELEASE_TAG = f"v{VERSION}"          # GitHub Release 的 tag
CHANGELOG = "更新内容:\n- 修复首页的问题"
# =========================================================

# GitHub 配置（一般不需要修改）
GITHUB_USER = "eroubisu"
GITHUB_REPO = "GameLobby-Client"
UPDATE_SERVER = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/client"
VERSION_FILE = "/version.json"

# 项目配置
APP_NAME = f"game_v{VERSION}"
MAIN_SCRIPT = "client.py"
ICON_FILE = "icon.ico"

# 自动生成下载链接
DOWNLOAD_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/{APP_NAME}.exe"

# PyInstaller 配置
PYINSTALLER_OPTIONS = [
    "--onefile",
    "--windowed",
    "--clean",
    "--noconfirm",
    f"--name={APP_NAME}",
]


def update_version_json(project_dir):
    """自动更新 client/version.json（从顶部配置同步）"""
    version_json_path = os.path.join(project_dir, 'client', 'version.json')
    
    # 直接使用顶部配置的值
    data = {
        "version": VERSION,
        "download_url": DOWNLOAD_URL,
        "changelog": CHANGELOG
    }
    
    with open(version_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已同步 client/version.json")
    print(f"  版本: {VERSION}")
    print(f"  下载: {DOWNLOAD_URL}")
    print(f"  日志: {CHANGELOG.split(chr(10))[0]}...")


def check_pyinstaller():
    """检查是否安装了 PyInstaller"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装 (版本 {PyInstaller.__version__})")
        return True
    except ImportError:
        print("✗ 未安装 PyInstaller")
        return False


def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("✓ PyInstaller 安装成功")
        return True
    else:
        print(f"✗ 安装失败: {result.stderr}")
        return False


def sync_version():
    """打包前写入版本配置"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 生成 version.txt
    version_file = os.path.join(base_dir, 'client', 'version.txt')
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(VERSION)
    print(f"✓ 版本文件已生成: client/version.txt (v{VERSION})")
    
    # 更新 config.py 中的更新服务器配置
    config_file = os.path.join(base_dir, 'client', 'config.py')
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    import re
    # 更新 UPDATE_SERVER
    content = re.sub(
        r'UPDATE_SERVER = "[^"]*"',
        f'UPDATE_SERVER = "{UPDATE_SERVER}"',
        content
    )
    # 更新 VERSION_FILE
    content = re.sub(
        r'VERSION_FILE = "[^"]*"',
        f'VERSION_FILE = "{VERSION_FILE}"',
        content
    )
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ 更新服务器配置已更新")


def restore_config():
    """打包后清理版本文件"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 删除 version.txt
    version_file = os.path.join(base_dir, 'client', 'version.txt')
    if os.path.exists(version_file):
        os.remove(version_file)
        print("✓ 已删除 client/version.txt")


def build():
    """执行打包"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("=" * 50)
    print(f"  游戏大厅客户端打包工具 v{VERSION}")
    print("=" * 50)
    print()
    
    # 检查主脚本是否存在
    if not os.path.exists(MAIN_SCRIPT):
        print(f"✗ 找不到主脚本: {MAIN_SCRIPT}")
        return False
    
    # 检查/安装 PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            return False
    
    # 同步版本号
    sync_version()
    
    print()
    print("开始打包...")
    print()
    
    # 构建命令
    cmd = [sys.executable, "-m", "PyInstaller"] + PYINSTALLER_OPTIONS
    
    # 添加图标（如果存在）
    if os.path.exists(ICON_FILE):
        cmd.append(f"--icon={ICON_FILE}")
        print(f"✓ 使用图标: {ICON_FILE}")
    
    # 添加数据文件
    cmd.append(f"--add-data=client;client")
    
    # 隐藏导入
    cmd.extend([
        "--hidden-import=client",
        "--hidden-import=client.chat_client",
        "--hidden-import=client.ui",
        "--hidden-import=client.network",
        "--hidden-import=client.config",
        "--hidden-import=client.avatar_editor",
        "--hidden-import=client.updater",
    ])
    
    # 主脚本
    cmd.append(MAIN_SCRIPT)
    
    print(f"执行命令: {' '.join(cmd)}")
    print()
    
    # 清理函数 - 尝试删除，失败则警告
    def cleanup():
        for cleanup_item in ['build', 'dist', f'{APP_NAME}.spec']:
            path = os.path.join(project_dir, cleanup_item)
            if not os.path.exists(path):
                continue
            
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
            except:
                pass
            
            # 检查是否删除成功
            if os.path.exists(path):
                print(f"  警告: 无法删除 {cleanup_item}，请手动删除")
    
    # 执行打包
    try:
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print()
            print("=" * 50)
            print("  ✓ 打包成功!")
            print("=" * 50)
            
            # 移动exe到根目录
            dist_file = os.path.join(project_dir, "dist", f"{APP_NAME}.exe")
            output_file = os.path.join(project_dir, f"{APP_NAME}.exe")
            
            if os.path.exists(dist_file):
                # 删除旧文件
                if os.path.exists(output_file):
                    os.remove(output_file)
                shutil.move(dist_file, output_file)
                
                file_size = os.path.getsize(output_file) / (1024 * 1024)
                print(f"  输出文件: {output_file}")
                print(f"  文件大小: {file_size:.2f} MB")
            
            # 自动更新 update_server/version.json
            update_version_json(project_dir)
            
            print()
            return True
        else:
            print()
            print("=" * 50)
            print("  ✗ 打包失败!")
            print("=" * 50)
            return False
    finally:
        # 无论成功失败都清理
        cleanup()
        restore_config()
        print("  已清理临时文件")


if __name__ == "__main__":
    success = build()
    
    if not success:
        print()
        print("如果遇到问题，请尝试:")
        print("  1. pip install --upgrade pyinstaller")
        print("  2. 确保所有依赖已安装")
        print("  3. 以管理员身份运行")
    
    input("\n按回车键退出...")
