/**
 * 💬 AI Chat - 前端交互核心逻辑 (SPA)
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- 全局状态 ---
    let currentSessionId = null;
    let currentProvider = "";
    let isGenerating = false;

    // --- DOM 节点索引 ---
    const sessionListEl = document.getElementById("session-list");
    const chatMessagesEl = document.getElementById("chat-messages");
    const chatInputEl = document.getElementById("chat-input");
    const sendBtnEl = document.getElementById("btn-send");
    const newChatBtnEl = document.getElementById("btn-new-chat");
    const modelSelectEl = document.getElementById("model-select");

    // 配置 Marked 选项（安全与解析设置）
    if (window.marked) {
        marked.setOptions({
            breaks: true,
            gfm: true,
        });
    }

    // --- 初始化入口 ---
    init();

    async function init() {
        await fetchProviders();
        await fetchSessions();
        setupEventListeners();
    }

    // --- 1. 获取并渲染可用模型 ---
    async function fetchProviders() {
        try {
            const res = await fetch("/api/providers");
            const data = await res.json();
            modelSelectEl.innerHTML = "";
            data.providers.forEach((p) => {
                const opt = document.createElement("option");
                opt.value = p;
                opt.textContent = p === "gemini" ? "✨ Gemini 3.6 Flash" : "🚀 DeepSeek V4";
                if (p === data.default) opt.selected = true;
                modelSelectEl.appendChild(opt);
            });
            currentProvider = modelSelectEl.value;
        } catch (err) {
            console.error("加载模型列表失败:", err);
        }
    }

    // --- 2. 获取并渲染历史会话列表 ---
    async function fetchSessions() {
        try {
            const res = await fetch("/api/sessions");
            const sessions = await res.json();
            renderSessionList(sessions);
        } catch (err) {
            console.error("加载会话列表失败:", err);
        }
    }

    function renderSessionList(sessions) {
        sessionListEl.innerHTML = "";
        if (!sessions || sessions.length === 0) {
            sessionListEl.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 10px;">暂无历史会话</div>`;
            return;
        }

        sessions.forEach((sess) => {
            const item = document.createElement("div");
            item.className = `session-item ${sess.id === currentSessionId ? "active" : ""}`;
            const timeStr = formatSessionTime(sess.updated_at);
            item.innerHTML = `
                <div class="session-info">
                    <span class="session-title-text" title="${escapeHtml(sess.title)}">${escapeHtml(sess.title)}</span>
                    <span class="session-time">${timeStr}</span>
                </div>
                <button class="btn-delete-session" title="删除会话">🗑️</button>
            `;

            // 点击切换会话
            item.addEventListener("click", (e) => {
                if (e.target.classList.contains("btn-delete-session")) return;
                loadSessionDetail(sess.id);
            });

            // 点击删除会话
            const delBtn = item.querySelector(".btn-delete-session");
            delBtn.addEventListener("click", async (e) => {
                e.stopPropagation();
                if (confirm(`确定要彻底删除会话 "${sess.title}" 吗？`)) {
                    await deleteSession(sess.id);
                }
            });

            sessionListEl.appendChild(item);
        });
    }

    // --- 3. 加载并展示特定会话历史 ---
    async function loadSessionDetail(sessionId) {
        try {
            const res = await fetch(`/api/sessions/${sessionId}`);
            if (!res.ok) return;
            const data = await res.json();
            currentSessionId = sessionId;

            // 自动匹配并切换顶部模型下拉菜单
            if (data.provider_name) {
                const targetProvider = data.provider_name.toLowerCase();
                for (let option of modelSelectEl.options) {
                    if (option.value.toLowerCase() === targetProvider) {
                        option.selected = true;
                        currentProvider = option.value;
                        break;
                    }
                }
            }

            // 清空当前消息区域，渲染历史消息
            chatMessagesEl.innerHTML = "";
            data.messages.forEach((msg) => {
                appendMessageCard(msg.role, msg.content, msg.created_at);
            });

            // 高亮选中的 sidebar item
            fetchSessions();
            scrollToBottom();
        } catch (err) {
            console.error("加载会话详情失败:", err);
        }
    }

    // --- 4. 删除会话 ---
    async function deleteSession(sessionId) {
        try {
            const res = await fetch(`/api/sessions/${sessionId}`, { method: "DELETE" });
            if (res.ok) {
                if (currentSessionId === sessionId) {
                    startNewChat();
                } else {
                    fetchSessions();
                }
            }
        } catch (err) {
            console.error("删除会话失败:", err);
        }
    }

    // --- 5. 开启新对话 ---
    function startNewChat() {
        currentSessionId = null;
        chatMessagesEl.innerHTML = `
            <div class="message-card assistant">
                <div class="avatar">🤖</div>
                <div class="message-body">
                    你好！我是你的 AI 助手。你可以问我任何问题，或者挑选顶部的模型开启新一轮对话！
                </div>
            </div>
        `;
        fetchSessions();
    }

    // --- 6. 发送消息与 SSE 帧动画打字机渲染 ---
    async function handleSend() {
        const question = chatInputEl.value.trim();
        if (!question || isGenerating) return;

        // 重置输入框
        chatInputEl.value = "";
        chatInputEl.style.height = "auto";
        setGeneratingState(true);

        // 如果是全新聊天且有欢迎卡片，先清空
        if (!currentSessionId && chatMessagesEl.children.length === 1 && chatMessagesEl.querySelector(".avatar").textContent === "🤖") {
            chatMessagesEl.innerHTML = "";
        }

        // 渲染用户问题
        appendMessageCard("user", question);
        scrollToBottom();

        // 创建 AI 助理占位卡片 (带闪烁光标)
        const assistantCard = document.createElement("div");
        assistantCard.className = "message-card assistant";
        assistantCard.innerHTML = `
            <div class="avatar">${currentProvider === "gemini" ? "✨" : "🚀"}</div>
            <div class="message-body"><span class="cursor"></span></div>
        `;
        chatMessagesEl.appendChild(assistantCard);
        const messageBodyEl = assistantCard.querySelector(".message-body");
        scrollToBottom();

        let rawAnswerText = "";
        let renderPending = false;
        let animationFrameId = null;

        // 💡 帧率节流渲染器：利用浏览器的刷新率绘制，避免没必要的高频 DOM 全量重绘
        function scheduleRender() {
            if (!renderPending) {
                renderPending = true;
                animationFrameId = requestAnimationFrame(() => {
                    const parsedMarkdown = renderMarkdown(rawAnswerText);
                    messageBodyEl.innerHTML = parsedMarkdown + '<span class="cursor"></span>';
                    scrollToBottom();
                    renderPending = false;
                });
            }
        }

        try {
            const response = await fetch("/api/chat/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: question,
                    session_id: currentSessionId,
                    provider: currentProvider,
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP 错误 ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || ""; // 最后一行为可能未接收完整的切片

                for (let line of lines) {
                    line = line.trim();
                    if (line.startsWith("data:")) {
                        const jsonStr = line.slice(5).trim();
                        if (!jsonStr) continue;
                        try {
                            const data = JSON.parse(jsonStr);
                            if (data.session_id) {
                                currentSessionId = data.session_id;
                            }
                            if (data.content === "[DONE]") {
                                continue;
                            }
                            if (data.content) {
                                rawAnswerText += data.content;
                                // 触发高效的帧更新
                                scheduleRender();
                            }
                        } catch (e) {
                            console.warn("解析 SSE 行失败:", line, e);
                        }
                    }
                }
            }

            // 处理 buffer 中剩余的最后一行数据
            if (buffer.trim().startsWith("data:")) {
                const jsonStr = buffer.trim().slice(5).trim();
                if (jsonStr) {
                    try {
                        const data = JSON.parse(jsonStr);
                        if (data.session_id) currentSessionId = data.session_id;
                        if (data.content && data.content !== "[DONE]") {
                            rawAnswerText += data.content;
                        }
                    } catch (e) { }
                }
            }

            // 对话结束，取消待处理的帧动画，渲染最终带时间戳的 Markdown
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
            const finalMarkdown = renderMarkdown(rawAnswerText);
            const nowTime = formatTime();
            messageBodyEl.innerHTML = `<div>${finalMarkdown}</div><div class="message-time">${nowTime}</div>`;
            fetchSessions(); // 刷新 sidebar 列表显示最新标题

        } catch (err) {
            console.error("流式生成异常:", err);
            messageBodyEl.innerHTML = `<span style="color: #ef4444;">❌ 无法获取回答: ${escapeHtml(err.message)}</span>`;
        } finally {
            if (animationFrameId) cancelAnimationFrame(animationFrameId);
            setGeneratingState(false);
            scrollToBottom();
        }
    }


    // --- 辅助工具函数 ---
    function appendMessageCard(role, content, timeVal) {
        const card = document.createElement("div");
        card.className = `message-card ${role}`;
        const avatarIcon = role === "user" ? "👤" : (currentProvider === "gemini" ? "✨" : "🚀");
        const renderedContent = renderMarkdown(content);
        const timeDisplay = formatTime(timeVal);

        card.innerHTML = `
            <div class="avatar">${avatarIcon}</div>
            <div class="message-body">
                <div>${renderedContent}</div>
                <div class="message-time">${timeDisplay}</div>
            </div>
        `;
        chatMessagesEl.appendChild(card);
    }


    function setGeneratingState(generating) {
        isGenerating = generating;
        sendBtnEl.disabled = generating;
        chatInputEl.disabled = generating;
    }

    function scrollToBottom() {
        chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
    }

    function escapeHtml(str) {
        return (str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function renderMarkdown(text) {
        if (!text) return "";
        const rawHtml = window.marked ? marked.parse(text) : escapeHtml(text);
        return window.DOMPurify ? DOMPurify.sanitize(rawHtml) : rawHtml;
    }

    function formatTime(timeVal) {
        if (!timeVal) {
            const now = new Date();
            return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
        }
        // 末尾补 'Z' 标识，确保浏览器按 UTC0 转换到本地东八区
        const parseStr = typeof timeVal === 'string' ? (timeVal.includes('Z') ? timeVal : timeVal.replace(' ', 'T') + 'Z') : timeVal;
        const date = new Date(parseStr);
        if (isNaN(date.getTime())) return timeVal;
        return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    }
    function formatSessionTime(timeVal) {
        if (!timeVal) return '';
        const parseStr = typeof timeVal === 'string' ? (timeVal.includes('Z') ? timeVal : timeVal.replace(' ', 'T') + 'Z') : timeVal;
        const date = new Date(parseStr);
        if (isNaN(date.getTime())) return timeVal;
        return `${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
    }

    // --- 事件监听配置 ---
    function setupEventListeners() {
        // 点击发送
        sendBtnEl.addEventListener("click", handleSend);

        // 标记输入法上字状态
        let isComposing = false;
        chatInputEl.addEventListener("compositionstart", () => { isComposing = true; });
        chatInputEl.addEventListener("compositionend", () => { isComposing = false; });
        // 回车发送 / Shift+Enter 换行 (自动过滤输入法选词回车)
        chatInputEl.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                if (e.isComposing || isComposing) {
                    return; // 如果正在使用输入法选词/上字，不触发发送
                }
                e.preventDefault();
                handleSend();
            }
        });

        // 输入框高度自动调整
        chatInputEl.addEventListener("input", () => {
            chatInputEl.style.height = "auto";
            chatInputEl.style.height = Math.min(chatInputEl.scrollHeight, 160) + "px";
        });

        // 切换模型选择
        modelSelectEl.addEventListener("change", (e) => {
            currentProvider = e.target.value;
        });

        // 开启新对话按钮
        newChatBtnEl.addEventListener("click", startNewChat);
    }
});
