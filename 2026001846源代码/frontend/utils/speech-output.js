/**
 * 语音播放工具 (TTS)
 * 调用后端 TTS 接口合成语音并通过 uni-app InnerAudioContext 播放。
 */

import { getBaseURL } from './request.js'

const normalizeError = (error, fallbackMessage) => {
  if (error instanceof Error) return error
  return new Error(error?.data?.message || error?.errMsg || error?.message || fallbackMessage)
}

export const createVoiceOutputController = (options = {}) => {
  let audioContext = null
  let isPlaying = false
  let isSynthesizing = false
  let currentText = ''

  const notifyState = (state) => {
    if (typeof options.onStateChange === 'function') {
      options.onStateChange(state)
    }
  }

  const destroyAudioContext = () => {
    if (audioContext) {
      try {
        audioContext.stop()
        audioContext.destroy()
      } catch (e) {}
      audioContext = null
    }
  }

  const getUserDataPath = () => {
    try { return wx.env.USER_DATA_PATH } catch (e) {}
    try { return uni.env.USER_DATA_PATH } catch (e) {}
    return '_doc'
  }

  const synthesizeText = (text) => {
    const baseURL = getBaseURL(options.service || 'tuantuan')
    const ttsUrl = baseURL + '/api/speech/tts'

    return new Promise((resolve, reject) => {
      uni.request({
        url: ttsUrl,
        method: 'POST',
        data: {
          text: text,
          voice: options.voice || 'zhichu',
          format: 'mp3'
        },
        responseType: 'arraybuffer',
        timeout: options.timeout || 30000,
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            const buffer = res.data
            if (!buffer) {
              reject(new Error('语音合成返回为空'))
              return
            }

            const fs = uni.getFileSystemManager()
            const filePath = `${getUserDataPath()}/tts_${Date.now()}.mp3`
            fs.writeFile({
              filePath,
              data: buffer,
              encoding: 'binary',
              success: () => resolve(filePath),
              fail: (err) => reject(new Error(err?.errMsg || '音频文件写入失败'))
            })
          } else {
            let msg = '语音合成失败'
            try {
              const decoder = new TextDecoder()
              const decoded = decoder.decode(new Uint8Array(res.data))
              const parsed = JSON.parse(decoded)
              msg = parsed.message || msg
            } catch (e) {}
            reject(new Error(msg))
          }
        },
        fail: (err) => reject(normalizeError(err, '语音合成请求失败'))
      })
    })
  }

  const playAudioFile = (filePath) => {
    return new Promise((resolve, reject) => {
      destroyAudioContext()

      audioContext = uni.createInnerAudioContext()
      audioContext.src = filePath

      audioContext.onEnded(() => {
        isPlaying = false
        notifyState({ isPlaying: false, isSynthesizing: false, text: currentText })
        resolve()
      })

      audioContext.onError((err) => {
        isPlaying = false
        notifyState({ isPlaying: false, isSynthesizing: false, text: '' })
        reject(normalizeError(err, '音频播放失败'))
      })

      audioContext.play()
    })
  }

  return {
    async speak(text) {
      if (!text || !text.trim()) return

      text = text.trim()
      if (text.length > 2000) {
        text = text.slice(0, 2000)
      }

      if (isPlaying) {
        this.stop()
      }

      currentText = text
      isSynthesizing = true
      notifyState({ isPlaying: false, isSynthesizing: true, text })

      try {
        const filePath = await synthesizeText(text)

        isSynthesizing = false
        isPlaying = true
        notifyState({ isPlaying: true, isSynthesizing: false, text })

        await playAudioFile(filePath)
      } catch (error) {
        isSynthesizing = false
        isPlaying = false
        notifyState({ isPlaying: false, isSynthesizing: false, text: '' })
        if (typeof options.onError === 'function') {
          options.onError(normalizeError(error, '语音播放失败'))
        }
        throw error
      }
    },

    stop() {
      destroyAudioContext()
      isPlaying = false
      isSynthesizing = false
      currentText = ''
      notifyState({ isPlaying: false, isSynthesizing: false, text: '' })
    },

    pause() {
      if (audioContext && isPlaying) {
        audioContext.pause()
        isPlaying = false
        notifyState({ isPlaying: false, isSynthesizing: false, text: currentText })
      }
    },

    resume() {
      if (audioContext && !isPlaying) {
        audioContext.play()
        isPlaying = true
        notifyState({ isPlaying: true, isSynthesizing: false, text: currentText })
      }
    },

    getState() {
      return { isPlaying, isSynthesizing, text: currentText }
    },

    destroy() {
      this.stop()
      audioContext = null
    }
  }
}
