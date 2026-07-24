import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts import SYSTEM_PROMPT
from logger import logger
from llm.base import BaseChatProvider
from typing import List, Dict


class GeminiProvider(BaseChatProvider):

    def __init__(self):
        super().__init__(provider_name="Gemini", model_name=GEMINI_MODEL)
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        logger.info(f"初始化 {self.provider_name} Provider，模型: {self.model_name}")

    def _truncate_history(self):
        """滑动窗口裁剪 Gemini 的内部 history"""
        max_history_msgs = self.max_history_turns * 2
        history = self.chat.get_history()
        if len(history) > max_history_msgs:
            # 直接截取最近的 max_history_msgs 条合规消息
            self.chat._history = history[-max_history_msgs:]
            logger.info(
                f"[{self.provider_name}] 触发上下文裁剪 ✂️: 保留最近 {self.max_history_turns} 轮对话"
            )

    def ask_stream(self, question: str):
        # 发送前先清理超长历史
        self._truncate_history()
        
        start_time = time.time()
        first_token_time = None
        start_len = len(self.chat.get_history())

        logger.info(
            f"[{self.provider_name}] 发起请求 -> 模型: {self.model_name} | 提问长度: {len(question)} 字符 | 历史轮数: {start_len}"
        )

        try:
            response = self.chat.send_message_stream(question)
            full_text = []

            for chunk in response:
                if chunk.text:
                    if first_token_time is None:
                        first_token_time = time.time()

                    full_text.append(chunk.text)
                    yield chunk.text

            total_cost = time.time() - start_time
            ttft = (first_token_time - start_time) if first_token_time else total_cost
            full_answer = "".join(full_text)

            logger.info(
                f"[{self.provider_name}] 请求成功 <- TTFT: {ttft:.2f}s | 总耗时: {total_cost:.2f}s | 回答长度: {len(full_answer)} 字符"
            )

            # 修复 SDK 缺陷：将流式产生的多 chunk 重新合并为 1 条合规的 model 消息
            history = self.chat.get_history()
            if len(history) > start_len:
                user_msg = history[start_len]
                merged_model_msg = types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=full_answer)]
                )
                self.chat._history = history[:start_len] + [user_msg, merged_model_msg]

        except Exception as e:
            logger.error(f"[{self.provider_name}] 请求失败 ❌: {str(e)}", exc_info=True)
            raise e

    def load_history(self, history_messages: List[Dict]):
        """加载历史消息，转换为 Gemini SDK 的 Content 对象并恢复 _history"""
        history_contents = []
        for msg in history_messages:
            # 映射角色: user -> user, assistant -> model
            role = "user" if msg["role"] == "user" else "model"
            content = types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
            history_contents.append(content)
        self.chat._history = history_contents
        # 载入后自动进行一次历史裁剪
        self._truncate_history()
        logger.info(f"[{self.provider_name}] 成功载入 {len(history_messages)} 条历史数据库消息")