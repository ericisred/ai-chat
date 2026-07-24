import sys
from chat import DeepSeekChatSession


def main():

    print("🤖 DeepSeek Chat 已启动")
    print("💡 输入 'exit' 退出\n")

    chat_session = DeepSeekChatSession()
    
    while True:
        try:
            question = input("你: ").strip()
            if not question:
                continue
        
            if question.lower() == "exit":
                print("👋 退出聊天")
                break

            print("\nDeepSeek: ",end="",flush=True)
            
            for chunk in chat_session.ask_stream(question):
                print(chunk,end="",flush=True)

            print("\n" + "-" * 50 + "\n")

        except (KeyboardInterrupt, EOFError):
            print("\n👋 退出聊天")
            sys.exit(0)


if __name__ == "__main__":
    main()