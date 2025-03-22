import speech_recognition as sr
from PyQt5.QtCore import QObject, pyqtSignal, QMutex

class VoiceRecognition(QObject):
    text_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.stop_listening = None
        self.mutex = QMutex()  # 修正1：正确初始化QMutex
        self._is_listening = False

        # 环境噪声校准（仅执行一次）
        print("校准麦克风...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    @property
    def is_listening(self):
        # 修正2：正确使用QMutex锁
        self.mutex.lock()
        state = self._is_listening
        self.mutex.unlock()
        return state

    @is_listening.setter
    def is_listening(self, value):
        self.mutex.lock()
        self._is_listening = value
        self.mutex.unlock()

    def start_listen(self):
        """安全启动语音监听"""
        if self.is_listening:
            return

        self.is_listening = True
        self._start_listening_thread()

    def stop_listen(self):
        """安全停止语音监听"""
        if not self.is_listening:
            return

        if self.stop_listening is not None:
            self.stop_listening(wait_for_stop=False)
            self.stop_listening = None
            
        self.is_listening = False

    def _start_listening_thread(self):
        """启动后台监听线程"""
        def callback(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio, language='zh-CN')
                self.text_received.emit(text)
            except sr.UnknownValueError:
                self.error_occurred.emit("无法识别语音")
            except sr.RequestError as e:
                self.error_occurred.emit(f"服务错误: {str(e)}")
            finally:
                if self.is_listening:
                    self._start_listening_thread()

        # 修正3：添加线程锁保护
        self.mutex.lock()
        try:
            self.stop_listening = self.recognizer.listen_in_background(
                self.microphone,
                callback,
                phrase_time_limit=5
            )
        finally:
            self.mutex.unlock()