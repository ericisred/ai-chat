import sys
from llm import LLMProviderFactory
from logger import logger 


def main():

    logger.info("================ AI Chat 应用程序启动 ================")

    # 通过工厂类获取当前配置激活的 LLM 实例（无需关心是 DeepSeek 还是 Gemini）
    chat_session = LLMProviderFactory.get_provider()
    print(f"🤖 {chat_session.provider_name} Chat ({chat_session.model_name}) 已启动")
    print("💡 输入 'exit' 退出\n")
    while True:
        try:
            question = input("你: ").strip()
            if not question:
                continue
            if question.lower() == "exit":
                logger.info("用户输入 'exit' 退出会话")
                print("👋 退出聊天")
                break
            print(f"\n{chat_session.provider_name}: ", end="", flush=True)
            # 统一面向接口调用 ask_stream 获得流式打字输出
            for chunk in chat_session.ask_stream(question):
                print(chunk, end="", flush=True)
            print("\n" + "-" * 50 + "\n")
        except (KeyboardInterrupt, EOFError):
            logger.info("用户触发快捷键 (Ctrl+C / Ctrl+D) 中断并退出程序")
            print("\n👋 退出聊天")
            sys.exit(0)


if __name__ == "__main__":
    main()