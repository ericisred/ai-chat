import sys
from llm import LLMProviderFactory
from memory import MemoryManager
from logger import logger


def select_or_create_session(
    memory_manager: MemoryManager,
) -> tuple[str, list, str]:
    """会话选单：引导用户开启新会话或恢复历史会话"""
    history_sessions = memory_manager.list_history_sessions(limit=5)

    print("=" * 50)
    print("📋 会话选单：")
    print("  [0] 开启新对话 (默认)")

    if history_sessions:
        for idx, sess in enumerate(history_sessions, start=1):
            print(
                f"  [{idx}] 恢复历史: {sess['title']} ({sess['updated_at']}) [{sess['provider_name']}]"
            )

    print("=" * 50)
    choice = input("请选择 [0-5] (直接回车默认开启新对话): ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(history_sessions):
        selected_sess = history_sessions[int(choice) - 1]
        session_id = selected_sess["id"]
        messages, summary = memory_manager.load_session(session_id)
        print(
            f"\n🔄 已成功恢复历史会话: [{selected_sess['title']}] (共 {len(messages)} 条历史记录 | 摘要长度: {len(summary)} 字符)\n"
        )
        return session_id, messages, summary
    else:
        # 准备新会话（延迟落盘）
        memory_manager.prepare_new_session()
        print("\n✨ 已准备开启新会话\n")
        return "", [], ""


def main():
    logger.info("================ AI Chat 应用程序启动 ================")

    try:
        chat_session = LLMProviderFactory.get_provider()
        memory_manager = MemoryManager()

        print(f"🤖 {chat_session.provider_name} Chat ({chat_session.model_name}) 已启动")
        print("💡 输入 'exit' 退出\n")

        session_id, history_messages, summary = select_or_create_session(memory_manager)

        if history_messages or summary:
            chat_session.load_history(history_messages, summary)

        while True:
            question = input("你: ").strip()
            if not question:
                continue

            if question.lower() == "exit":
                logger.info("用户输入 'exit' 退出会话")
                print("👋 退出聊天")
                break

            print(f"\n{chat_session.provider_name}: ", end="", flush=True)

            full_answer = ""
            for chunk in chat_session.ask_stream(question):
                full_answer += chunk
                print(chunk, end="", flush=True)

            print("\n" + "-" * 50 + "\n")

            # 4. 对话成功后持久化落盘（传入最新的 summary）
            memory_manager.save_turn(
                question,
                full_answer,
                chat_session.provider_name,
                chat_session.model_name,
                chat_session.summary,
            )

    except (KeyboardInterrupt, EOFError):
        logger.info("用户触发快捷键 (Ctrl+C / Ctrl+D) 中断并退出程序")
        print("\n👋 退出聊天")
        sys.exit(0)



if __name__ == "__main__":
    main()
