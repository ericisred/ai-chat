import time
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from prompts import build_system_prompt, SUMMARY_PROMPT
from logger import logger
from llm.base import BaseChatProvider
from typing import List, Dict


class DeepSeekProvider(BaseChatProvider):

    def __init__(self):
        super().__init__(provider_name="DeepSeek", model_name=DEEPSEEK_MODEL)
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        self.messages = [
            {"role": "system", "content": build_system_prompt(self.summary)}
        ]
        logger.info(f"初始化 {self.provider_name} Provider，模型: {self.model_name}")

    def _generate_incremental_summary(self, old_messages: List[Dict]) -> str:
        """调用 DeepSeek 针对旧对话做增量摘要压缩"""
        formatted_dialogue = []
        for msg in old_messages:
            role_str = "用户" if msg["role"] == "user" else "助手"
            formatted_dialogue.append(f"{role_str}: {msg['content']}")

        dialogue_text = "\n".join(formatted_dialogue)
        prompt = f"{SUMMARY_PROMPT.strip()}\n\n【现有历史摘要】：\n{self.summary or '无'}\n\n【新增的早期对话片段】：\n{dialogue_text}\n\n请输出最新的综合增量摘要："

        logger.info(f"[{self.provider_name}] 正在触发 LLM 生成滚动记忆摘要 🔄...")
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            new_summary = response.choices[0].message.content.strip()
            logger.info(f"[{self.provider_name}] 滚动摘要生成成功 💡:\n{new_summary}")
            return new_summary
        except Exception as e:
            logger.error(f"[{self.provider_name}] 滚动摘要生成失败: {e}", exc_info=True)
            return self.summary

    def _truncate_messages(self):
        """滑动窗口裁剪与滚动摘要生成"""
        trigger_msgs = self.summary_trigger_turns * 2
        keep_msgs = self.recent_keep_turns * 2

        # 除去首位 System Prompt 后的实际对话消息
        dialogue_msgs = self.messages[1:]

        if len(dialogue_msgs) > trigger_msgs:
            old_messages = dialogue_msgs[:-keep_msgs]
            recent_msgs = dialogue_msgs[-keep_msgs:]

            # 生成最新摘要
            self.summary = self._generate_incremental_summary(old_messages)

            # 更新首位 System Prompt
            system_msg = {"role": "system", "content": build_system_prompt(self.summary)}
            self.messages = [system_msg] + recent_msgs

            logger.info(
                f"[{self.provider_name}] 触发滚动摘要 ✂️: 压缩前 {len(old_messages)//2} 轮对话，保留最近 {self.recent_keep_turns} 轮明细"
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

    def load_history(self, history_messages: List[Dict], summary: str = ""):
        """加载历史消息与摘要，覆盖重建 self.messages（保持首位带 Summary 的 System Prompt）"""
        self.summary = summary
        system_msg = {"role": "system", "content": build_system_prompt(self.summary)}
        self.messages = [system_msg]
        for msg in history_messages:
            self.messages.append({"role": msg["role"], "content": msg["content"]})
        # 载入后自动进行一次历史裁剪与摘要检查
        self._truncate_messages()
        logger.info(f"[{self.provider_name}] 成功载入 {len(history_messages)} 条历史数据库消息，摘要长度: {len(self.summary)} 字符")