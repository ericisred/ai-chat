from chat import ask_gemini


def main():

    print("Gemini Chat 已启动")
    print("输入 'exit' 退出\n")
    
    while True:

        question = input("你: ")
        
        if question.lower() == "exit":
            print("退出聊天")
            break

        answer = ask_gemini(question)
        print("\nGemini: ")
        print(answer)
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()