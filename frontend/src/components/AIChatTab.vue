<template>
  <div class="chat-tab">
    <!-- Message list -->
    <div ref="messagesRef" class="chat-messages">
      <div v-if="!messages.length" class="chat-welcome">
        <div class="welcome-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="32" height="32">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <p class="welcome-text">基于视频内容的 AI 问答</p>
        <p class="welcome-hint">你可以询问关于视频内容的任何问题</p>
        <div class="quick-questions">
          <button
            v-for="q in quickQuestions"
            :key="q"
            class="quick-btn"
            @click="sendMessage(q)"
          >
            {{ q }}
          </button>
        </div>
      </div>

      <div
        v-for="(msg, idx) in messages"
        :key="idx"
        class="message"
        :class="msg.role"
      >
        <div class="msg-avatar">
          <span v-if="msg.role === 'user'">你</span>
          <span v-else>AI</span>
        </div>
        <div class="msg-body">
          <MarkdownProse
            v-if="msg.role === 'assistant'"
            class="msg-content"
            :source="msg.content"
            compact
          />
          <div v-else class="msg-content">{{ msg.content }}</div>
          <div v-if="msg.role === 'assistant' && msg.streaming" class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="chat-input-bar">
      <input
        v-model="inputText"
        type="text"
        class="chat-input"
        placeholder="输入你的问题..."
        @keydown.enter="handleSend"
        :disabled="streaming"
      />
      <button
        class="send-btn"
        @click="handleSend"
        :disabled="!inputText.trim() || streaming"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from "vue";
import { streamChat } from "../api/ai.js";
import MarkdownProse from "./MarkdownProse.vue";

const props = defineProps({
  transcript: { type: String, default: "" },
  title: { type: String, default: "" },
});

const quickQuestions = [
  "这个视频的主要内容是什么？",
  "视频中有哪些关键知识点？",
  "总结视频的核心结论",
];

const messages = reactive([]);
const inputText = ref("");
const streaming = ref(false);
const messagesRef = ref(null);

let currentController = null;

function handleSend() {
  if (!inputText.value.trim() || streaming.value) return;
  sendMessage(inputText.value.trim());
  inputText.value = "";
}

function sendMessage(text) {
  messages.push({ role: "user", content: text });

  const assistantMsg = reactive({
    role: "assistant",
    content: "",
    streaming: true,
  });
  messages.push(assistantMsg);
  streaming.value = true;
  scrollToBottom();

  const chatMessages = messages
    .filter((m) => !m.streaming || m === assistantMsg)
    .filter((m) => m.role === "user" || (m.role === "assistant" && m.content))
    .map((m) => ({ role: m.role, content: m.content }));

  const messagesForApi = chatMessages.slice(0, -1);

  if (currentController) {
    currentController.abort();
  }

  currentController = streamChat(
    {
      transcript: props.transcript,
      title: props.title,
      messages: messagesForApi,
    },
    {
      onChunk(chunk) {
        assistantMsg.content += chunk;
        scrollToBottom();
      },
      onDone() {
        assistantMsg.streaming = false;
        streaming.value = false;
        scrollToBottom();
      },
      onError(msg) {
        assistantMsg.content = assistantMsg.content || `抱歉，出现错误: ${msg}`;
        assistantMsg.streaming = false;
        streaming.value = false;
        scrollToBottom();
      },
    }
  );
}

async function scrollToBottom() {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
}
</script>

<style scoped>
.chat-tab {
  display: flex;
  flex-direction: column;
  height: 480px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Welcome */

.chat-welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  gap: 8px;
}

.welcome-icon {
  color: var(--text-muted);
  opacity: 0.5;
}

.welcome-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.welcome-hint {
  font-size: 13px;
  color: var(--text-muted);
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  justify-content: center;
}

.quick-btn {
  padding: 8px 16px;
  font-size: 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.quick-btn:hover {
  border-color: var(--accent-blue);
  color: var(--accent-blue);
  background: var(--accent-blue-light);
}

/* Messages */

.message {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
}

.message.user .msg-avatar {
  background: var(--accent-blue);
  color: #fff;
}

.message.assistant .msg-avatar {
  background: linear-gradient(135deg, #ede9fe, #dbeafe);
  color: #7c3aed;
}

.msg-body {
  max-width: 80%;
  min-width: 0;
}

.msg-content {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 13px;
  line-height: 1.7;
}

.message.user .msg-content {
  background: var(--accent-blue);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.message.assistant .msg-content {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
}

.message.assistant .msg-content.md-prose :deep(p:last-child) {
  margin-bottom: 0;
}

/* Typing indicator */

.typing-indicator {
  display: flex;
  gap: 4px;
  padding-top: 6px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing-dot 1.2s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-dot {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* Input */

.chat-input-bar {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
  margin-top: 8px;
}

.chat-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  font-size: 13px;
  outline: none;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-family: inherit;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: var(--accent-blue);
}

.chat-input::placeholder {
  color: var(--text-muted);
}

.send-btn {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent-blue);
  color: #fff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-blue-hover);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .chat-tab {
    height: 400px;
  }

  .msg-body {
    max-width: 85%;
  }
}
</style>
