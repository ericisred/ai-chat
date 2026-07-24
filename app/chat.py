import time

from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME
from prompts import SYSTEM_PROMPT
from logger import logger


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
        logger.info(f"初始化 ChatSession，使用模型: {MODEL_NAME}")


    def ask_stream(self, question: str):
        # 2. 将当前用户提问追加到历史中
        self.messages.append({"role": "user", "content": question})

        start_time = time.time()
        first_token_time = None
        logger.info(f"发起请求 -> 模型: {MODEL_NAME} | 提问长度: {len(question)} 字符 | 当前历史轮数: {len(self.messages)}")

        try:
            # 3. 发起 OpenAI 兼容接口的流式请求
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=self.messages,
                stream=True
            )

            full_answer = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    # 记录首包时间 (TTFT)
                    if first_token_time is None:
                        first_token_time = time.time()
                    
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    yield content

            total_cost = time.time() - start_time
            ttft = (first_token_time - start_time) if first_token_time else total_cost
            # 记录成功的请求耗时
            logger.info(
                f"请求成功 <- 首包耗时(TTFT): {ttft:.2f}s | 总耗时: {total_cost:.2f}s | 回答长度: {len(full_answer)} 字符"
            )

            # 4. 完整的回答生成后，追加到历史列表中，自动维系多轮对话
            self.messages.append({"role": "assistant", "content": full_answer})

        except Exception as e:
            logger.error(f"请求失败 ❌ - 错误信息: {str(e)}", exc_info=True)
            raise e

