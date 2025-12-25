"""
局域网JRPG聊天室 - 客户端入口
"""

from client.chat_client import ChatClient


def main():
    client = ChatClient()
    client.run()


if __name__ == '__main__':
    main()
