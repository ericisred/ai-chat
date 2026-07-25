import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_MODEL
from prompts import build_system_prompt, SUMMARY_PROMPT
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
                system_instruction=build_system_prompt(self.summary)
            )
        )
        logger.info(f"初始化 {self.provider_name} Provider，模型: {self.model_name}")

    def _generate_incremental_summary(self, old_messages: List[types.Content]) -> str:
        """调用 Gemini 针对旧对话做增量摘要压缩"""
        formatted_dialogue = []
        for msg in old_messages:
            role_str = "用户" if msg.role == "user" else "助手"
            text_content = "".join([p.text for p in msg.parts if p.text])
            formatted_dialogue.append(f"{role_str}: {text_content}")

        dialogue_text = "\n".join(formatted_dialogue)
        prompt = f"{SUMMARY_PROMPT.strip()}\n\n【现有历史摘要】：\n{self.summary or '无'}\n\n【新增的早期对话片段】：\n{dialogue_text}\n\n请输出最新的综合增量摘要："

        logger.info(f"[{self.provider_name}] 正在触发 LLM 生成滚动记忆摘要 🔄...")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            new_summary = response.text.strip()
            logger.info(f"[{self.provider_name}] 滚动摘要生成成功 💡:\n{new_summary}")
            return new_summary
        except Exception as e:
            logger.error(f"[{self.provider_name}] 滚动摘要生成失败: {e}", exc_info=True)
            return self.summary

    def _truncate_history(self):
        """滑动窗口裁剪与滚动摘要生成"""
        trigger_msgs = self.summary_trigger_turns * 2
        keep_msgs = self.recent_keep_turns * 2
        history = self.chat.get_history(curated=True)

        if len(history) > trigger_msgs:
            old_messages = history[:-keep_msgs]
            recent_history = list(history[-keep_msgs:])

            # 生成最新增量摘要
            self.summary = self._generate_incremental_summary(old_messages)

            # 动态更新 System Prompt 保持记忆生效
            self.chat._config.system_instruction = build_system_prompt(self.summary)

            # 裁剪历史明细
            self.chat._curated_history = recent_history
            self.chat._comprehensive_history = recent_history
            logger.info(
                f"[{self.provider_name}] 触发滚动摘要 ✂️: 压缩前 {len(old_messages)//2} 轮对话，保留最近 {self.recent_keep_turns} 轮明细"
            )

    def ask_stream(self, question: str):
        # 发送前先清理超长历史并生成摘要
        self._truncate_history()
        
        start_time = time.time()
        first_token_time = None
        start_len = len(self.chat.get_history(curated=True))

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

            # 显式构造本轮 user 消息与合并后的 model 消息，绕过 SDK 流式 is_valid 校验失败的 BUG
            user_msg = types.Content(
                role="user",
                parts=[types.Part.from_text(text=question)]
            )
            merged_model_msg = types.Content(
                role="model",
                parts=[types.Part.from_text(text=full_answer)]
            )

            # 正确更新 SDK 内部的 _curated_history 与 _comprehensive_history
            curated = list(self.chat.get_history(curated=True)[:start_len])
            self.chat._curated_history = curated + [user_msg, merged_model_msg]
            self.chat._comprehensive_history = list(self.chat._curated_history)

        except Exception as e:
            logger.error(f"[{self.provider_name}] 请求失败 ❌: {str(e)}", exc_info=True)
            raise e

    def load_history(self, history_messages: List[Dict], summary: str = ""):
        """加载历史消息及摘要，转换为 Gemini SDK 的 Content 对象并恢复 _curated_history / _comprehensive_history"""
        self.summary = summary
        self.chat._config.system_instruction = build_system_prompt(self.summary)

        history_contents = []
        for msg in history_messages:
            # 映射角色: user -> user, assistant -> model
            role = "user" if msg["role"] == "user" else "model"
            content = types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
            history_contents.append(content)
        self.chat._curated_history = history_contents
        self.chat._comprehensive_history = list(history_contents)
        # 载入后自动进行一次历史裁剪
        self._truncate_history()
        logger.info(f"[{self.provider_name}] 成功载入 {len(history_messages)} 条历史记录，摘要长度: {len(self.summary)} 字符")