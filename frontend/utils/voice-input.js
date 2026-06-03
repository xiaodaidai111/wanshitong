import { uploadFile } from './request.js'

const DEFAULT_RECORD_OPTIONS = {
  duration: 60000,
  sampleRate: 16000,
  numberOfChannels: 1,
  encodeBitRate: 96000,
  format: 'mp3'
}

const DEFAULT_ASR_MODEL = 'paraformer-v2'

const normalizeError = (error, fallbackMessage) => {
  if (error instanceof Error) return error
  return new Error(error?.data?.message || error?.errMsg || error?.message || fallbackMessage)
}

export const createVoiceInputController = (options = {}) => {
  const recorderFactory = typeof uni !== 'undefined' && typeof uni.getRecorderManager === 'function'
  if (!recorderFactory) {
    return {
      startRecording() {
        return Promise.reject(new Error('当前环境不支持语音录制'))
      },
      stopRecording() {
        return Promise.reject(new Error('当前环境不支持语音录制'))
      },
      toggleRecording() {
        return Promise.reject(new Error('当前环境不支持语音录制'))
      },
      destroy() {},
      getState() {
        return { isRecording: false, isStopping: false, isTranscribing: false }
      }
    }
  }

  const recorder = uni.getRecorderManager()
  let isRecording = false
  let isStopping = false
  let isTranscribing = false
  let pendingResolve = null
  let pendingReject = null
  let stopTimer = null

  const bindRecorderEvents = () => {
    if (typeof recorder.offStop === 'function') {
      recorder.offStop(handleStop)
    }
    if (typeof recorder.offError === 'function') {
      recorder.offError(handleError)
    }
    recorder.onStop(handleStop)
    recorder.onError(handleError)
  }

  const notifyState = () => {
    if (typeof options.onStateChange === 'function') {
      options.onStateChange({ isRecording, isStopping, isTranscribing })
    }
  }

  const clearStopTimer = () => {
    if (stopTimer) {
      clearTimeout(stopTimer)
      stopTimer = null
    }
  }

  const handleStop = async (result) => {
    clearStopTimer()
    const resolve = pendingResolve
    const reject = pendingReject
    pendingResolve = null
    pendingReject = null
    isRecording = false
    isStopping = false
    notifyState()

    if (!resolve || !reject) {
      return
    }

    const tempFilePath = result?.tempFilePath
    if (!tempFilePath) {
      const error = normalizeError(result, '录音文件生成失败')
      if (typeof options.onError === 'function') {
        options.onError(error)
      }
      reject(error)
      return
    }

    try {
      isTranscribing = true
      notifyState()

      const response = await uploadFile(
        options.transcribePath || '/api/speech/transcribe',
        tempFilePath,
        options.fieldName || 'audio',
        {
          service: options.service || 'tuantuan',
          timeout: options.timeout || 120000,
          formData: {
            model: options.model || DEFAULT_ASR_MODEL
          }
        }
      )

      const text = (response?.data?.text || response?.text || '').trim()
      if (!text) {
        throw new Error(response?.message || '语音识别结果为空')
      }

      if (typeof options.onTranscribed === 'function') {
        options.onTranscribed(text, response)
      }

      resolve({ text, response })
    } catch (error) {
      const normalizedError = normalizeError(error, '语音识别失败')
      if (typeof options.onError === 'function') {
        options.onError(normalizedError)
      }
      reject(normalizedError)
    } finally {
      isTranscribing = false
      notifyState()
    }
  }

  const handleError = (error) => {
    clearStopTimer()
    const normalizedError = normalizeError(error, '录音失败')
    isRecording = false
    isStopping = false
    isTranscribing = false
    notifyState()

    if (typeof options.onError === 'function') {
      options.onError(normalizedError)
    }

    if (pendingReject) {
      pendingReject(normalizedError)
    }
    pendingResolve = null
    pendingReject = null
  }

  bindRecorderEvents()

  return {
    async startRecording() {
      if (isTranscribing) {
        throw new Error('语音识别中，请稍候')
      }

      if (isStopping) {
        throw new Error('正在停止录音，请稍候')
      }

      if (isRecording) {
        return
      }

      bindRecorderEvents()
      recorder.start({
        ...DEFAULT_RECORD_OPTIONS,
        ...(options.recordOptions || {})
      })
      isRecording = true
      notifyState()

      if (typeof options.onStart === 'function') {
        options.onStart()
      }
    },

    stopRecording() {
      if (isStopping) {
        return Promise.reject(new Error('正在停止录音，请稍候'))
      }

      if (!isRecording) {
        return Promise.reject(new Error('当前未在录音'))
      }

      return new Promise((resolve, reject) => {
        pendingResolve = resolve
        pendingReject = reject
        isRecording = false
        isStopping = true
        notifyState()

        bindRecorderEvents()
        stopTimer = setTimeout(() => {
          pendingResolve = null
          pendingReject = null
          isStopping = false
          const error = new Error('录音停止超时，请重试')
          notifyState()
          reject(error)
          if (typeof options.onError === 'function') {
            options.onError(error)
          }
        }, options.stopTimeout || 10000)

        try {
          recorder.stop()
        } catch (error) {
          clearStopTimer()
          pendingResolve = null
          pendingReject = null
          isStopping = false
          notifyState()
          reject(normalizeError(error, '停止录音失败'))
        }
      })
    },

    async toggleRecording() {
      if (isRecording) {
        return this.stopRecording()
      }

      await this.startRecording()
      return null
    },

    destroy() {
      clearStopTimer()
      if (isRecording || isStopping) {
        try {
          recorder.stop()
        } catch (error) {}
      }
      if (typeof recorder.offStop === 'function') {
        recorder.offStop(handleStop)
      }
      if (typeof recorder.offError === 'function') {
        recorder.offError(handleError)
      }
      pendingResolve = null
      pendingReject = null
      isRecording = false
      isStopping = false
      isTranscribing = false
      notifyState()
    },

    getState() {
      return { isRecording, isStopping, isTranscribing }
    }
  }
}
