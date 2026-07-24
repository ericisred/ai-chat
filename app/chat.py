from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME
from prompts import SYSTEM_PROMPT


class DeepSeekChatSession:

    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        # 1. 初始化标准对话历史，首位为系统提示词 (System Prompt)
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def ask_stream(self, question: str):
        # 2. 将当前用户提问追加到历史中
        self.messages.append({"role": "user", "content": question})

        # 3. 发起 OpenAI 兼容接口的流式请求
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.messages,
            stream=True
        )

        full_answer = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_answer += content
                yield content

        # 4. 完整的回答生成后，追加到历史列表中，自动维系多轮对话
        self.messages.append({"role": "assistant", "content": full_answer})
