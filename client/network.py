"""
网络通信模块
"""

import socket
import json
import threading


class NetworkManager:
    """网络管理"""
    
    def __init__(self, port):
        self.socket = None
        self.port = port
        self.connected = False
        self.receive_callback = None
        self.disconnect_callback = None
    
    def connect(self, host):
        """连接服务器"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.socket.connect((host, self.port))
        self.socket.settimeout(None)
        self.connected = True
        return True
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def send(self, data):
        """发送数据"""
        if not self.connected:
            return False
        try:
            msg = json.dumps(data) + '\n'
            self.socket.send(msg.encode('utf-8'))
            return True
        except:
            return False
    
    def start_receive_loop(self, callback):
        """启动接收循环"""
        self.receive_callback = callback
        thread = threading.Thread(target=self._receive_loop)
        thread.daemon = True
        thread.start()
    
    def _receive_loop(self):
        """接收循环"""
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                buffer += data.decode('utf-8')
                while '\n' in buffer:
                    msg_str, buffer = buffer.split('\n', 1)
                    if msg_str:
                        try:
                            msg = json.loads(msg_str)
                            if self.receive_callback:
                                self.receive_callback(msg)
                        except json.JSONDecodeError:
                            pass
            except:
                break
        
        self.connected = False
        if self.disconnect_callback:
            self.disconnect_callback()
