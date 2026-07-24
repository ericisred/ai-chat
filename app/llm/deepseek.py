import time
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from prompts import SYSTEM_PROMPT
from logger import logger
from llm.base import BaseChatProvider


class DeepSeekProvider(BaseChatProvider):

    def __init__(self):
        super().__init__(provider_name="DeepSeek", model_name=DEEPSEEK_MODEL)
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        self.messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        logger.info(f"初始化 {self.provider_name} Provider，模型: {self.model_name}")

    def _truncate_messages(self):
        """滑动窗口裁剪：保留 system_prompt + 最近 max_history_turns 轮对话"""
        max_history_msgs = self.max_history_turns * 2
        # 如果消息总数（除去 system_prompt）超过最大限制，进行裁剪
        if len(self.messages) - 1 > max_history_msgs:
            system_msg = self.messages[0]  # 永远保留首位的 System Prompt
            recent_msgs = self.messages[-max_history_msgs:]  # 截取最近 N 轮
            self.messages = [system_msg] + recent_msgs
            logger.info(
                f"[{self.provider_name}] 触发上下文裁剪 ✂️: 保留首位 System Prompt + 最近 {self.max_history_turns} 轮对话"
            )

    def ask_stream(self, question: str):
        self.messages.append({"role": "user", "content": question})

        self._truncate_messages()
        
        start_time = time.time()
        first_token_time = None

        logger.info(
            f"[{self.provider_name}] 发起请求 -> 模型: {self.model_name} | 提问长度: {len(question)} 字符 | 历史轮数: {len(self.messages)}"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
                stream=True
            )

            full_answer = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    if first_token_time is None:
                        first_token_time = time.time()

                    content = chunk.choices[0].delta.content
                    full_answer += content
                    yield content

            total_cost = time.time() - start_time
            ttft = (first_token_time - start_time) if first_token_time else total_cost
            logger.info(
                f"[{self.provider_name}] 请求成功 <- TTFT: {ttft:.2f}s | 总耗时: {total_cost:.2f}s | 回答长度: {len(full_answer)} 字符"
            )

            self.messages.append({"role": "assistant", "content": full_answer})

        except Exception as e:
            logger.error(f"[{self.provider_name}] 请求失败 ❌: {str(e)}", exc_info=True)
            raise e
