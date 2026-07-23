from chat import ask_gemini_stream


def main():

    print("Gemini Chat 已启动")
    print("输入 'exit' 退出\n")
    
    while True:

        question = input("你: ").strip()
        if not question:
            continue
        
        if question.lower() == "exit":
            print("退出聊天")
            break
        print("\nGemini: ",end="",flush=True)
        for chunk in ask_gemini_stream(question):
            print(chunk,end="",flush=True)

        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()