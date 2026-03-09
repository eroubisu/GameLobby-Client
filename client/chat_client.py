"""
聊天客户端主类
"""

import tkinter as tk
from tkinter import messagebox

from .config import (
    PORT, WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_SIZE,
    enable_dpi_awareness, init_fonts,
    COLOR_BG_PRIMARY
)
from .network import NetworkManager
from .ui import LoginUI, GameUI
from .avatar_editor import AvatarEditor
try:
    from .config import VERSION
except ImportError:
    VERSION = None


class ChatClient:
    """聊天客户端"""
    
    def __init__(self):
        # 启用 DPI 感知（必须在创建窗口前调用）
        enable_dpi_awareness()
        
        self.network = NetworkManager(PORT)
        self.player_data = None
        self.pending_messages = []
        self.current_channel = 1
        
        self.root = tk.Tk()
        self.root.title(f"{WINDOW_TITLE}" + (f" v{VERSION}" if VERSION else ""))
        self.root.geometry(WINDOW_SIZE)
        self.root.minsize(*WINDOW_MIN_SIZE)
        self.root.configure(bg=COLOR_BG_PRIMARY)
        
        # 初始化字体（检测可用字体）
        init_fonts(self.root)
        
        self.login_ui = None
        self.game_ui = None
        
        # 先显示登录界面（按钮禁用）
        self.login_ui = LoginUI(self.root, self._on_connect)
        
        # 后台检查更新
        self._check_update_async()
    
    def _check_update_async(self):
        """后台检查更新，完成后在主线程启用连接按钮"""
        import threading
        
        def _do_check():
            try:
                from .updater import check_for_update, UpdateDialog
                has_update, latest_version, download_url, changelog = check_for_update()
                
                if has_update:
                    # 需要更新 - 在主线程显示更新对话框
                    self.root.after(0, lambda: self._show_update_dialog(
                        latest_version, changelog, download_url))
                else:
                    # 已是最新版本 - 启用连接按钮
                    self.root.after(0, self._on_update_check_ok)
            except Exception as e:
                print(f"检查更新时出错: {e}")
                # 出错时也允许连接
                self.root.after(0, self._on_update_check_ok)
        
        threading.Thread(target=_do_check, daemon=True).start()
    
    def _on_update_check_ok(self):
        """更新检查通过，启用连接按钮"""
        if self.login_ui:
            self.login_ui.enable_connect()
    
    def _show_update_dialog(self, latest_version, changelog, download_url):
        """显示更新对话框"""
        from .updater import UpdateDialog
        if self.login_ui:
            self.login_ui.set_update_status("发现新版本，请更新", '#ff6b6b')
        UpdateDialog(self.root, latest_version, changelog, download_url)
    
    def _on_connect(self, ip):
        try:
            self.network.connect(ip)
            self.network.start_receive_loop(self._on_message)
            
            self.login_ui.destroy()
            self.game_ui = GameUI(
                self.root,
                on_chat=self._send_chat,
                on_command=self._send_command,
                on_switch_channel=self._switch_channel
            )
            
            # 设置窗口关闭事件处理（二次确认）
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)
            
            self.root.update()
            
            for msg in self.pending_messages:
                self._display_message(msg)
            self.pending_messages.clear()
            
        except Exception as e:
            messagebox.showerror("连接失败", str(e))
    
    def _on_close(self):
        """窗口关闭事件处理（游戏中需二次确认）"""
        if self.game_ui and self.game_ui.in_mahjong_game:
            # 麻将游戏进行中，二次确认
            if messagebox.askyesno("确认退出", "游戏正在进行中，确定要退出吗？\n\n退出将会被记为逃跑！"):
                self._force_close()
        else:
            self._force_close()
    
    def _force_close(self):
        """强制关闭窗口"""
        try:
            self.network.disconnect()
        except:
            pass
        self.root.destroy()
    
    def _show_win_animation(self, msg):
        """显示胜利动画（逐条显示役种）"""
        winner = msg.get('winner', '?')
        win_type = msg.get('win_type', 'tsumo')
        tile = msg.get('tile', '?')
        loser = msg.get('loser', '')
        yakus = msg.get('yakus', [])
        han = msg.get('han', 0)
        fu = msg.get('fu', 0)
        score = msg.get('score', 0)
        is_yakuman = msg.get('is_yakuman', False)
        
        # 第一条消息：胜利宣言
        if win_type == 'tsumo':
            header = f"【{winner} 自摸】 [{tile}]"
        else:
            header = f"【{winner} 荣和】 [{tile}]" + (f" (放铳: {loser})" if loser else "")
        
        self.game_ui.add_game_message(header)
        
        # 逐条显示役种（每条间隔 800ms）
        delay = 800
        for i, yaku in enumerate(yakus):
            yaku_name = yaku[0]
            yaku_han = yaku[1]
            is_yaku_yakuman = yaku[2] if len(yaku) > 2 else False
            
            if is_yaku_yakuman:
                yaku_text = f"  ★ {yaku_name} (役满)"
            else:
                yaku_text = f"  · {yaku_name} ({yaku_han}番)"
            
            self.root.after(delay * (i + 1), lambda t=yaku_text: self.game_ui.add_game_message(t))
        
        # 最后显示总点数（在所有役种显示完后）
        final_delay = delay * (len(yakus) + 1)
        if is_yakuman:
            score_text = f"\n【点数】役满 {score}点"
        else:
            score_text = f"\n【点数】{han}番{fu}符 = {score}点"
        
        self.root.after(final_delay, lambda: self.game_ui.add_game_message(score_text))
        self.root.after(final_delay + 400, lambda: self.game_ui.add_game_message("\n输入 /next 开始下一局"))
    
    def _send_chat(self, text, channel):
        """发送聊天消息（纯聊天，不处理指令）"""
        self.network.send({'type': 'chat', 'text': text, 'channel': channel})
    
    def _send_command(self, text):
        """发送游戏指令"""
        self.network.send({'type': 'command', 'text': text})
    
    def _switch_channel(self, channel_id):
        """切换频道"""
        self.current_channel = channel_id
        self.network.send({'type': 'switch_channel', 'channel': channel_id})
    
    def _open_avatar_editor(self):
        """打开头像编辑器"""
        def on_avatar_complete(avatar_data):
            # 发送头像数据到服务器
            self.network.send({'type': 'avatar_update', 'avatar': avatar_data})
            self.game_ui.add_game_message('头像已保存！')
        
        AvatarEditor(self.root, on_avatar_complete)
    
    def _on_message(self, msg):
        if not self.game_ui:
            self.pending_messages.append(msg)
            return
        self.root.after(0, lambda: self._display_message(msg))
    
    def _display_message(self, msg):
        if not self.game_ui:
            return
        
        try:
            msg_type = msg.get('type', 'chat')
            
            if msg_type == 'login_prompt':
                # 登录提示显示在指令区
                self.game_ui.add_game_message(msg['text'])
            
            elif msg_type == 'request_avatar':
                # 服务器请求头像，打开头像编辑器
                self.game_ui.add_game_message(msg['text'])
                self._open_avatar_editor()
                
            elif msg_type == 'login_success':
                # 登录成功
                self.game_ui.set_logged_in()
                self.game_ui.add_game_message(msg['text'])
                
            elif msg_type == 'system':
                self.game_ui.add_system_message(msg['text'])
                
            elif msg_type == 'game':
                # 游戏消息/命令响应输出到当前窗口
                update_last = msg.get('update_last', False)
                self.game_ui.add_game_message(msg['text'], to_main=False, update_last=update_last)
                # 如果需要清除出牌状态（如确认退出提示）
                if msg.get('clear_discard'):
                    self.game_ui.need_discard = False
                    self.game_ui.set_cmd_prefix('/')
                
            elif msg_type == 'chat':
                name = msg.get('name', '???')
                channel = msg.get('channel', 1)
                time_str = msg.get('time', '')  # 获取时间戳
                self.game_ui.add_chat_message(name, msg['text'], channel, time_str)
            
            elif msg_type == 'chat_history':
                # 聊天历史记录
                channel = msg.get('channel', 1)
                messages = msg.get('messages', [])
                self.game_ui.show_chat_history(messages, channel)
            
            elif msg_type == 'status':
                self.player_data = msg.get('data', {})
                self.game_ui.update_status(self.player_data)
                if 'map' in msg and msg['map']:
                    self.game_ui.update_map(msg['map'])
            
            elif msg_type == 'online_users':
                users = msg.get('users', [])
                self.game_ui.update_online_users(users)
            
            elif msg_type == 'game_invite':
                # 游戏邀请通知
                self.game_ui.show_game_invite(msg)
            
            elif msg_type == 'room_update':
                # 麻将房间更新
                room_data = msg.get('room_data')
                if room_data:
                    self.game_ui.update_table(room_data)
                    # 保存房间ID用于位置显示
                    room_id = room_data.get('room_id')
                    if room_id:
                        self.game_ui.current_room_id = room_id
                    # 检查是否在游戏中（用于退出确认）
                    state = room_data.get('state', 'waiting')
                    self.game_ui.set_mahjong_mode(state == 'playing')
                message = msg.get('message')
                if message:
                    self.game_ui.add_game_message(message)
            
            elif msg_type == 'room_leave':
                # 离开房间，切回大头像视图
                self.game_ui.update_table(None)
                self.game_ui.clear_hand()
                self.game_ui.set_mahjong_mode(False)
                self.game_ui.current_room_id = None  # 清除房间ID
                # 更新位置
                location = msg.get('location')
                if location:
                    self.game_ui.set_location(location)
            
            elif msg_type == 'game_quit':
                # 退出游戏返回大厅
                self.game_ui.update_table(None)
                self.game_ui.clear_hand()
                self.game_ui.set_mahjong_mode(False)
                self.game_ui.current_room_id = None  # 清除房间ID
                # 更新位置
                location = msg.get('location')
                if location:
                    self.game_ui.set_location(location)
            
            elif msg_type == 'location_update':
                # 位置更新
                location = msg.get('location')
                if location:
                    self.game_ui.set_location(location)
            
            elif msg_type == 'hand_update':
                # 手牌更新
                hand = msg.get('hand', [])
                drawn = msg.get('drawn')  # 新摸的牌
                tenpai_analysis = msg.get('tenpai_analysis')  # 听牌分析
                need_discard = msg.get('need_discard', False)  # 是否需要出牌
                self.game_ui.update_hand(hand, drawn, tenpai_analysis, need_discard)
            
            elif msg_type == 'action_prompt':
                # 吃碰杠操作提示
                actions = msg.get('actions', {})
                tile = msg.get('tile', '')
                from_player = msg.get('from_player', '')
                self.game_ui.show_action_prompt(actions, tile, from_player)
            
            elif msg_type == 'self_action_prompt':
                # 立直/暗杠/加杠/自摸操作提示
                actions = msg.get('actions', {})
                self.game_ui.show_self_action_prompt(actions)
            
            elif msg_type == 'win_animation':
                # 胜利动画（逐条显示役种）
                self._show_win_animation(msg)
            
            elif msg_type == 'action':
                action = msg.get('action', '')
                if action == 'clear':
                    self.game_ui.clear_game_area()
                elif action == 'version':
                    # 显示版本信息
                    server_version = msg.get('server_version', '未知')
                    client_version = VERSION if VERSION else '开发版'
                    version_info = f"📋 版本信息\n\n客户端版本: v{client_version}\n服务器版本: v{server_version}"
                    self.game_ui.add_game_message(version_info)
                elif action == 'exit':
                    self.network.disconnect()
                    self.root.destroy()
                elif action == 'maintenance':
                    messagebox.showwarning("系统维护", "服务器正在进行每日维护，请稍后重新连接。")
                    self.network.disconnect()
                    self.root.destroy()
        except:
            pass
    
    def run(self):
        self.root.mainloop()
        self.network.disconnect()
