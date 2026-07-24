import sys
from chat import DeepSeekChatSession
from logger import logger 


def main():

    logger.info("================ AI Chat 应用程序启动 ================")

    print("🤖 DeepSeek Chat 已启动")
    print("💡 输入 'exit' 退出\n")

    chat_session = DeepSeekChatSession()
    
    while True:
        try:
            question = input("你: ").strip()
            if not question:
                continue
        
            if question.lower() == "exit":
                logger.info("用户输入 'exit' 退出会话")
                print("👋 退出聊天")
                break

            print("\nDeepSeek: ",end="",flush=True)
            
            for chunk in chat_session.ask_stream(question):
                print(chunk,end="",flush=True)

            print("\n" + "-" * 50 + "\n")

        except (KeyboardInterrupt, EOFError):
            logger.info("用户触发快捷键 (Ctrl+C / Ctrl+D) 中断并退出程序")
            print("\n👋 退出聊天")
            sys.exit(0)


if __name__ == "__main__":
    main()