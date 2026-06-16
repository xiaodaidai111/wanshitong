<template>
  <view class="health-manager-fab">
    <view
      class="fab-btn"
      :class="{
        'fab-dragging': isDragging,
        'fab-snapping': isSnapping
      }"
      :style="fabStyle"
      @touchstart.stop="onPointerDown"
      @touchmove.stop="onPointerMove"
      @touchend.stop="onPointerEnd"
      @touchcancel.stop="onPointerEnd"
      @mousedown.stop.prevent="onMouseDown"
      @click.stop="onClick"
    >
      <image class="fab-image" src="/static/assistant-maintenance.png" mode="aspectFill"></image>
      <view class="fab-badge" v-if="unreadCount > 0">
        <text class="badge-text">{{ unreadCount > 99 ? '99+' : unreadCount }}</text>
      </view>
      <view class="fab-pulse" v-if="!isDragging && !isExpanded"></view>
    </view>

    <view
      class="chat-panel"
      :class="{ 'panel-visible': isExpanded }"
      :style="panelStyle"
      @touchstart.stop
      @touchmove.stop
      @touchend.stop
      @mousedown.stop
    >
      <view class="panel-header">
        <view class="header-left">
          <view class="bot-avatar">
            <image class="avatar-image" src="/static/assistant-maintenance.png" mode="aspectFill"></image>
          </view>
          <view class="bot-info">
            <text class="bot-name">{{ ui.botName }}</text>
            <text class="bot-status">{{ ui.botStatus }}</text>
          </view>
        </view>
        <view class="header-right" @click="collapsePanel">
          <text class="close-icon">{{ ui.closeText }}</text>
        </view>
      </view>

      <scroll-view
        class="chat-history"
        scroll-y
        :scroll-top="scrollTop"
        scroll-with-animation
      >
        <view class="message-list">
          <view
            v-for="(msg, index) in messages"
            :key="index"
            class="message-item"
            :class="msg.role === 'user' ? 'message-user' : 'message-bot'"
          >
            <view class="message-bubble">
              <text class="message-text">{{ msg.content }}</text>
            </view>
          </view>
          <view v-if="isTyping" class="message-item message-bot">
            <view class="message-bubble typing-bubble">
              <text class="typing-dot">.</text>
              <text class="typing-dot">.</text>
              <text class="typing-dot">.</text>
            </view>
          </view>
        </view>
      </scroll-view>

      <view class="quick-replies" v-if="isExpanded && quickReplies.length > 0 && messages.length <= 2">
        <view
          class="quick-reply-item"
          v-for="(reply, index) in quickReplies"
          :key="index"
          @click="sendQuickReply(reply)"
        >
          <text class="quick-reply-text">{{ reply }}</text>
        </view>
      </view>

      <view class="input-area">
        <input
          class="chat-input"
          type="text"
          v-model="inputText"
          :placeholder="ui.placeholder"
          confirm-type="send"
          @confirm="sendMessage"
          :disabled="isTyping"
        />
        <view
          class="voice-btn"
          @click="toggleVoiceInput"
          :class="{ active: isVoiceRecording || isVoiceTranscribing, disabled: isTyping }"
        >
          <text class="voice-text">{{ isVoiceRecording ? "停止" : (isVoiceTranscribing ? "识别中" : "语音") }}</text>
        </view>
        <view class="send-btn" @click="sendMessage" :class="{ disabled: !inputText.trim() || isTyping }">
          <text class="send-text">{{ isTyping ? '...' : ui.sendText }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from "@/utils/request"
import { createVoiceInputController } from "@/utils/voice-input"

const EDGE_PADDING = 16
const SNAP_DURATION = 250
const MOVE_THRESHOLD = 5
const FAB_SIZE_RPX = 120
const now = () => {
  if (typeof performance !== "undefined" && typeof performance.now === "function") {
    return performance.now()
  }
  return Date.now()
}
const raf = (callback) => {
  if (typeof requestAnimationFrame === "function") {
    return requestAnimationFrame(callback)
  }
  return setTimeout(() => callback(now()), 16)
}
const caf = (id) => {
  if (typeof cancelAnimationFrame === "function") {
    cancelAnimationFrame(id)
    return
  }
  clearTimeout(id)
}

const UI_TEXT = {
  botName: "\u53f8\u5357\u68c0\u4fee\u52a9\u624b",
  botStatus: "\u4efb\u52a1\u95ed\u73af\u00b7\u98ce\u9669\u6392\u67e5",
  closeText: "\u00d7",
  placeholder: "\u8f93\u5165\u8bbe\u5907\u6545\u969c\u6216\u4efb\u52a1\u8fdb\u5c55...",
  sendText: "\u53d1\u9001",
  busyText: "\u62b1\u6b49\uff0c\u53f8\u5357\u68c0\u4fee\u52a9\u624b\u6b63\u5728\u6574\u7406\u4efb\u52a1\u4fe1\u606f\uff0c\u8bf7\u7a0d\u540e\u518d\u8bd5\u3002",
  networkErrorText: "\u8fde\u63a5\u53f8\u5357\u68c0\u4fee\u52a9\u624b\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u7f51\u7edc\u8fde\u63a5\u3002"
}
const DEFAULT_BOT_MESSAGE = "\u4f60\u597d\uff0c\u6211\u662f\u53f8\u5357\u68c0\u4fee\u52a9\u624b\u3002\u6211\u53ef\u4ee5\u5e2e\u4f60\u68b3\u7406\u5f85\u5904\u7406\u4efb\u52a1\u3001\u5206\u6790\u6545\u969c\u98ce\u9669\u3001\u63a8\u8350\u6807\u51c6\u4f5c\u4e1a\u6d41\u7a0b\uff0c\u5e76\u63d0\u9192\u5f85\u9a8c\u6536\u548c\u8d85\u65f6\u9879\u3002"
const DEFAULT_QUICK_REPLIES = [
  "\u5e2e\u6211\u68b3\u7406\u4eca\u65e5\u5f85\u5904\u7406\u4efb\u52a1",
  "\u54ea\u4e9b\u68c0\u4fee\u4efb\u52a1\u9700\u8981\u4f18\u5148\u95ed\u73af\uff1f",
  "\u914d\u7535\u67dc\u8fc7\u70ed\u68c0\u4fee\u6d41\u7a0b",
  "\u5982\u4f55\u8865\u9f50\u5f85\u9a8c\u6536\u8bb0\u5f55\uff1f"
]

export default {
  name: "HealthManagerFab",
  props: {
    initialPosition: {
      type: Object,
      default: () => ({ right: 40, bottom: 200 })
    },
    pageContext: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      isDragging: false,
      isSnapping: false,
      isExpanded: false,
      position: { x: 0, y: 0 },
      fabSizePx: 60,
      windowWidth: 0,
      windowHeight: 0,
      unreadCount: 0,
      ui: UI_TEXT,
      messages: [{ role: "bot", content: DEFAULT_BOT_MESSAGE }],
      inputText: "",
      isTyping: false,
      isVoiceRecording: false,
      isVoiceTranscribing: false,
      voiceInputController: null,
      scrollTop: 0,
      quickReplies: [...DEFAULT_QUICK_REPLIES],
      startPointerX: 0,
      startPointerY: 0,
      startPosX: 0,
      startPosY: 0,
      hasMoved: false,
      isMouseDown: false,
      rafId: null
    }
  },
  mounted() {
    this.messages = [{ role: "bot", content: DEFAULT_BOT_MESSAGE }]
    this.quickReplies = [...DEFAULT_QUICK_REPLIES]
    this.initSystemInfo()
    this.initVoiceInput()
    this._bindGlobalMouseEvents()
  },
  beforeDestroy() {
    if (this.voiceInputController) {
      this.voiceInputController.destroy()
    }
    this._unbindGlobalMouseEvents()
    if (this.rafId) {
      caf(this.rafId)
      this.rafId = null
    }
  },
  computed: {
    fabStyle() {
      return {
        left: this.position.x + "px",
        top: this.position.y + "px",
        width: this.fabSizePx + "px",
        height: this.fabSizePx + "px"
      }
    },
    panelStyle() {
      const panelWidth = Math.min(this.windowWidth * 0.85, 350)
      const panelHeight = Math.min(this.windowHeight * 0.65, 560)
      const panelGap = 12

      let left = this.position.x + this.fabSizePx + panelGap
      let top = this.position.y + panelHeight / 2 - this.fabSizePx / 2

      if (left + panelWidth > this.windowWidth - EDGE_PADDING) {
        left = this.position.x - panelWidth - panelGap
      }

      if (left < EDGE_PADDING) {
        left = EDGE_PADDING
      }

      if (top + panelHeight > this.windowHeight - EDGE_PADDING) {
        top = this.windowHeight - panelHeight - EDGE_PADDING
      }

      if (top < EDGE_PADDING) {
        top = EDGE_PADDING
      }

      return {
        left: left + "px",
        top: top + "px",
        width: panelWidth + "px",
        height: panelHeight + "px"
      }
    }
  },
  methods: {
    initVoiceInput() {
      if (this.voiceInputController) return

      this.voiceInputController = createVoiceInputController({
        service: "tuantuan",
        onStateChange: ({ isRecording, isTranscribing }) => {
          this.isVoiceRecording = isRecording
          this.isVoiceTranscribing = isTranscribing
        },
        onTranscribed: (text) => {
          this.inputText = this.inputText.trim() ? `${this.inputText.trim()} ${text}` : text
          uni.showToast({ title: "语音已转文字", icon: "none" })
        },
        onError: (error) => {
          const title = (error?.message || "语音输入失败").slice(0, 20)
          uni.showToast({ title, icon: "none" })
        }
      })
    },

    initSystemInfo() {
      const sys = uni.getSystemInfoSync()
      this.windowWidth = sys.windowWidth
      this.windowHeight = sys.windowHeight
      this.fabSizePx = uni.upx2px(FAB_SIZE_RPX)

      this.position.x = this.windowWidth - this.fabSizePx - uni.upx2px(this.initialPosition.right)
      this.position.y = this.windowHeight - this.fabSizePx - uni.upx2px(this.initialPosition.bottom)

      this.snapToEdge(false)
    },

    _getPointerXY(e) {
      if (e.touches && e.touches.length > 0) {
        return { x: e.touches[0].clientX, y: e.touches[0].clientY }
      }
      if (e.changedTouches && e.changedTouches.length > 0) {
        return { x: e.changedTouches[0].clientX, y: e.changedTouches[0].clientY }
      }
      return { x: e.clientX || 0, y: e.clientY || 0 }
    },

    onPointerDown(e) {
      if (this.isExpanded) return
      const { x, y } = this._getPointerXY(e)
      this.isDragging = true
      this.hasMoved = false
      this.startPointerX = x
      this.startPointerY = y
      this.startPosX = this.position.x
      this.startPosY = this.position.y
    },

    onMouseDown(e) {
      if (this.isExpanded) return
      this.isMouseDown = true
      const { x, y } = this._getPointerXY(e)
      this.isDragging = true
      this.hasMoved = false
      this.startPointerX = x
      this.startPointerY = y
      this.startPosX = this.position.x
      this.startPosY = this.position.y
    },

    onPointerMove(e) {
      if (!this.isDragging) return
      const { x, y } = this._getPointerXY(e)
      this._updatePosition(x, y)
    },

    _onGlobalMouseMove(e) {
      if (!this.isDragging || !this.isMouseDown) return
      const { x, y } = this._getPointerXY(e)
      this._updatePosition(x, y)
    },

    _onGlobalMouseUp(e) {
      if (!this.isMouseDown) return
      this.isMouseDown = false
      if (this.isDragging) {
        this.onPointerEnd(e)
      }
    },

    _updatePosition(pointerX, pointerY) {
      const dx = pointerX - this.startPointerX
      const dy = pointerY - this.startPointerY

      if (Math.sqrt(dx * dx + dy * dy) > MOVE_THRESHOLD) {
        this.hasMoved = true
      }

      let newX = this.startPosX + dx
      let newY = this.startPosY + dy

      const maxX = this.windowWidth - this.fabSizePx
      const maxY = this.windowHeight - this.fabSizePx

      this.position.x = Math.max(0, Math.min(newX, maxX))
      this.position.y = Math.max(0, Math.min(newY, maxY))
    },

    onPointerEnd() {
      if (!this.isDragging) return
      this.isDragging = false
      this.snapToEdge(true)
    },

    snapToEdge(animate) {
      const centerX = this.position.x + this.fabSizePx / 2
      let targetX

      if (centerX < this.windowWidth / 2) {
        targetX = EDGE_PADDING
      } else {
        targetX = this.windowWidth - this.fabSizePx - EDGE_PADDING
      }

      let targetY = this.position.y
      const maxY = this.windowHeight - this.fabSizePx - EDGE_PADDING
      if (targetY < EDGE_PADDING) {
        targetY = EDGE_PADDING
      }
      if (targetY > maxY) {
        targetY = maxY
      }

      if (animate) {
        this.isSnapping = true
        const startX = this.position.x
        const startY = this.position.y
        const startTime = now()

        const animateStep = (currentTime) => {
          const frameTime = typeof currentTime === "number" ? currentTime : now()
          const elapsed = frameTime - startTime
          const progress = Math.min(elapsed / SNAP_DURATION, 1)
          const eased = 1 - Math.pow(1 - progress, 3)

          this.position.x = startX + (targetX - startX) * eased
          this.position.y = startY + (targetY - startY) * eased

          if (progress < 1) {
            this.rafId = raf(animateStep)
          } else {
            this.isSnapping = false
            this.rafId = null
          }
        }

        if (this.rafId) {
          caf(this.rafId)
        }
        this.rafId = raf(animateStep)
      } else {
        this.position.x = targetX
        this.position.y = targetY
      }
    },

    onClick() {
      if (this.hasMoved) {
        this.hasMoved = false
        return
      }
      this.expandPanel()
    },

    expandPanel() {
      this.isExpanded = true
      this.scrollToBottom()
    },

    collapsePanel() {
      this.isExpanded = false
    },

    scrollToBottom() {
      setTimeout(() => {
        this.scrollTop = 99999
      }, 100)
    },

    sendQuickReply(text) {
      this.inputText = text
      this.sendMessage()
    },

    async toggleVoiceInput() {
      this.initVoiceInput()

      try {
        await this.voiceInputController.toggleRecording()
      } catch (error) {
        const title = (error?.message || "语音输入失败").slice(0, 20)
        uni.showToast({ title, icon: "none" })
      }
    },

    async ensureConversation() {
      if (this._convId) return
      try {
        const res = await request.post("/api/chat/conversations", {})
        if (res?.data?.conversation_id) {
          this._convId = res.data.conversation_id
        }
      } catch (e) {
        // 忽略，使用空conversation_id
      }
    },

    async sendMessage() {
      const text = this.inputText.trim()
      if (!text || this.isTyping) return

      await this.ensureConversation()

      this.messages.push({ role: "user", content: text })
      this.inputText = ""
      this.scrollToBottom()

      this.isTyping = true

      try {
        const res = await request.post("/api/chat/messages", {
          conversation_id: this._convId || '',
          message: text,
          page_context: this.pageContext
        })

        const reply = res?.data?.response || res?.response
        const convId = res?.data?.conversation_id
        if (convId) this._convId = convId

        if (reply) {
          this.messages.push({ role: "bot", content: reply })
        } else {
          this.messages.push({ role: "bot", content: this.ui.busyText })
        }
        this.scrollToBottom()
        uni.vibrateShort()
      } catch (e) {
        console.error("Chat error:", e)
        this.messages.push({ role: "bot", content: this.ui.networkErrorText })
        this.scrollToBottom()
      } finally {
        this.isTyping = false
      }
    },

    _bindGlobalMouseEvents() {
      if (typeof window !== "undefined") {
        this._boundGlobalMouseMove = this._onGlobalMouseMove.bind(this)
        this._boundGlobalMouseUp = this._onGlobalMouseUp.bind(this)
        window.addEventListener("mousemove", this._boundGlobalMouseMove, { passive: false })
        window.addEventListener("mouseup", this._boundGlobalMouseUp, { passive: false })
      }
    },

    _unbindGlobalMouseEvents() {
      if (typeof window !== "undefined") {
        window.removeEventListener("mousemove", this._boundGlobalMouseMove)
        window.removeEventListener("mouseup", this._boundGlobalMouseUp)
      }
    }
  }
}
</script>

<style scoped>
.health-manager-fab {
  position: fixed;
  top: 0;
  left: 0;
  pointer-events: none;
  width: 100%;
  height: 100%;
  z-index: var(--z-index-floating, 100);
}

.fab-btn {
  position: absolute;
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10rpx 28rpx rgba(16, 185, 129, 0.24);
  pointer-events: auto;
  z-index: calc(var(--z-index-floating, 100) + 1);
  overflow: hidden;
  border: 4rpx solid #ffffff;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  touch-action: none;
  will-change: transform, left, top;
}

.fab-btn:active {
  cursor: grabbing;
}

.fab-image {
  width: 100%;
  height: 100%;
}

.fab-dragging {
  transform: scale(1.12);
  box-shadow: 0 16rpx 40rpx rgba(0, 0, 0, 0.25);
  transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
  z-index: calc(var(--z-index-floating, 100) + 10);
}

.fab-snapping {
  transition:
    left 0.25s cubic-bezier(0.25, 1, 0.5, 1),
    top 0.25s cubic-bezier(0.25, 1, 0.5, 1);
}

.fab-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.32) 0%, transparent 70%);
  animation: fab-pulse 2.5s ease-in-out infinite;
  z-index: -1;
  pointer-events: none;
}

@keyframes fab-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 0.4;
  }
  50% {
    transform: scale(1.35);
    opacity: 0.8;
  }
}

.fab-badge {
  position: absolute;
  top: -4rpx;
  right: -4rpx;
  background-color: #ef4444;
  color: white;
  min-width: 32rpx;
  height: 32rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid white;
  z-index: 2;
  padding: 0 6rpx;
}

.badge-text {
  font-size: 20rpx;
  line-height: 1;
}

.chat-panel {
  position: fixed;
  background-color: white;
  border-radius: 20rpx;
  box-shadow: 0 8rpx 40rpx rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  transform: scale(0.5);
  opacity: 0;
  pointer-events: auto;
  overflow: hidden;
  z-index: var(--z-index-dialog, 1000);
  transition:
    transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
    opacity 0.25s ease-out;
  transform-origin: bottom left;
}

.panel-visible {
  transform: scale(1);
  opacity: 1;
}

.panel-header {
  padding: 24rpx 30rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2rpx solid #f0f0f0;
  background-color: #fff;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.bot-avatar {
  background-color: #ECFDF5;
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.avatar-image {
  width: 100%;
  height: 100%;
}

.bot-info {
  display: flex;
  flex-direction: column;
}

.bot-name {
  font-weight: bold;
  font-size: 30rpx;
  color: #0f172a;
}

.bot-status {
  font-size: 22rpx;
  color: #10b981;
}

.close-icon {
  font-size: 36rpx;
  color: #9ca3af;
  padding: 10rpx;
  cursor: pointer;
}

.chat-history {
  flex: 1;
  background-color: #f9fafb;
  height: 0;
  padding: 20rpx 0;
}

.message-list {
  padding: 0 24rpx 20rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.message-item {
  display: flex;
  max-width: 82%;
  width: fit-content;
}

.message-user {
  align-self: flex-end;
  justify-content: flex-end;
  margin-left: auto;
}

.message-bot {
  align-self: flex-start;
  justify-content: flex-start;
}

.message-bubble {
  padding: 20rpx 28rpx;
  border-radius: 28rpx;
  word-break: break-all;
}

.message-text {
  font-size: 26rpx;
  line-height: 1.5;
}

.message-user .message-bubble {
  background: linear-gradient(135deg, #2563eb 0%, #10b981 100%);
  color: white;
  border-bottom-right-radius: 4rpx;
}

.message-bot .message-bubble {
  background-color: white;
  border: 2rpx solid #e5e7eb;
  color: #374151;
  border-bottom-left-radius: 4rpx;
}

.typing-bubble {
  flex-direction: row;
  display: flex;
  gap: 8rpx;
  padding: 20rpx 28rpx;
}

.typing-dot {
  animation: bounce 1.4s infinite ease-in-out both;
  font-size: 28rpx;
  color: #9ca3af;
}

.typing-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 16rpx 24rpx;
  padding-bottom: calc(16rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background-color: white;
  border-top: 2rpx solid #f0f0f0;
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex-shrink: 0;
}

.quick-replies {
  padding: 16rpx 24rpx;
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  background-color: #f9fafb;
  border-top: 2rpx solid #f0f0f0;
  flex-shrink: 0;
}

.quick-reply-item {
  background-color: white;
  border: 2rpx solid #10b981;
  border-radius: 28rpx;
  padding: 10rpx 20rpx;
  transition: all 0.2s;
  cursor: pointer;
}

.quick-reply-item:active {
  background-color: #10b981;
  transform: scale(0.95);
}

.quick-reply-item:active .quick-reply-text {
  color: white;
}

.quick-reply-text {
  font-size: 22rpx;
  color: #059669;
  font-weight: 500;
}

.chat-input {
  flex: 1;
  background-color: #f3f4f6;
  height: 72rpx;
  border-radius: 36rpx;
  padding: 0 28rpx;
  font-size: 26rpx;
}

.chat-input:disabled {
  opacity: 0.6;
}

.voice-btn {
  min-width: 110rpx;
  height: 72rpx;
  padding: 0 20rpx;
  border-radius: 36rpx;
  background-color: #ECFDF5;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1rpx solid #BBF7D0;
  transition: all 0.2s;
}

.voice-btn.active {
  background-color: #10b981;
  border-color: #10b981;
}

.voice-btn.disabled {
  opacity: 0.6;
}

.voice-text {
  font-size: 22rpx;
  color: #047857;
  font-weight: 600;
}

.voice-btn.active .voice-text {
  color: white;
}

.send-btn {
  background: linear-gradient(135deg, #2563eb 0%, #10b981 100%);
  color: white;
  padding: 0 28rpx;
  height: 72rpx;
  border-radius: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
  cursor: pointer;
}

.send-text {
  font-size: 24rpx;
  font-weight: 600;
}

.send-btn.disabled {
  opacity: 0.5;
  background-color: #9ca3af;
}
</style>
