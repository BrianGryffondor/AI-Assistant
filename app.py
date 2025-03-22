import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QThread, pyqtSignal
from audio_utils import VoiceRecognition
from api_client import DeepSeekClient
import os
from PyQt5.QtWidgets import QFileDialog
from PyPDF2 import PdfReader
from docx import Document
import pdfplumber  # 更先进的PDF解析

# 新增工作线程类
class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client, prompt):
        super().__init__()
        self.client = client
        self.prompt = prompt
         # 文件解析上下文
        self.file_context = ""

    def run(self):
        try:
            response = self.client.chat(self.prompt)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ai_client = DeepSeekClient()
        self.voice_recog = VoiceRecognition()
        self.init_ui()
        self.connect_signals()
        
        # 初始化计时器
        self.response_timer = QTimer()
        self.response_timer.timeout.connect(self.update_response_time)
        self.elapsed_seconds = 0

    def init_ui(self):
        # 窗口设置（保持原有样式不变）
        self.setWindowTitle("AI小助手")
        self.setGeometry(300, 300, 800, 600)
        
        # 聊天区域（保持原有样式不变）
        self.chat_area = QTextEdit(readOnly=True)
        self.chat_area.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                line-height: 1.5;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        
        # 输入区域（保持原有样式不变）
        self.input_area = QTextEdit()
        self.input_area.setMaximumHeight(100)
        self.input_area.setPlaceholderText("输入问题或按住语音按钮开始说话...")
        self.input_area.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # 功能按钮（保持原有样式不变）
        self.voice_btn = QPushButton("🎤 按住说话")
        self.file_btn = QPushButton("📁 上传文件")
        self.send_btn = QPushButton("发送")
        
        
        # 状态栏（保持原有样式不变）
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignRight)
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        
        # 按钮样式（保持原有样式不变）
        button_style = """
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 12px 24px;
                border-radius: 5px;
                min-width: 120px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:checked {
                background-color: #f44336;
            }
            QPushButton:pressed {
                background-color: #367c2b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """
        self.voice_btn.setStyleSheet(button_style)
        self.send_btn.setStyleSheet(button_style.replace("#4CAF50", "#2196F3"))
        
        # 布局设置（保持原有样式不变）
        button_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.voice_btn.setSizePolicy(button_size_policy)
        self.send_btn.setSizePolicy(button_size_policy)
        self.file_btn.setSizePolicy(button_size_policy)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.voice_btn)
        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.file_btn)
        btn_layout.setSpacing(15)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.chat_area)
        main_layout.addWidget(self.input_area)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)

    def connect_signals(self):
        self.voice_btn.toggled.connect(self.on_voice_toggle)
        self.send_btn.clicked.connect(self.on_send_click)
        self.file_btn.clicked.connect(self.handle_file_upload)
        self.voice_recog.text_received.connect(self.update_input)
        self.voice_recog.error_occurred.connect(self.show_error)

    def handle_file_upload(self):
        """处理文件上传"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "支持格式 (*.pdf *.docx *.txt);;PDF文件 (*.pdf);;Word文件 (*.docx);;文本文件 (*.txt)"
        )
        
        if file_path:
            self._process_file(file_path)

    def _process_file(self, file_path):
        """解析文件内容"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.pdf':
                content = self._parse_pdf(file_path)
            elif ext == '.docx':
                content = self._parse_docx(file_path)
            elif ext == '.txt':
                content = self._parse_txt(file_path)
            else:
                raise ValueError("不支持的文件格式")
                
            self.file_context = content[:5000]  # 保留前5000字符
            self._append_message("📂 系统", f"已成功解析文件：{os.path.basename(file_path)}")
            
        except Exception as e:
            self.show_error(f"文件解析失败：{str(e)}")

    def _parse_pdf(self, file_path):
        """解析PDF文件"""
        text = ""
        try:
            # 使用pdfplumber获取更精准的文本
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except:
            # 回退到PyPDF2
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                text = "\n".join([page.extract_text() for page in reader.pages])
        return text.strip()

    def _parse_docx(self, file_path):
        """解析Word文档"""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _parse_txt(self, file_path):
        """解析纯文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @pyqtSlot(bool)
    def on_voice_toggle(self, checked):
        if checked:
            self.voice_btn.setText("正在聆听...")
            self.voice_recog.start_listen()
        else:
            self.voice_btn.setText("🎤 按住说话")
            self.voice_recog.stop_listen()

    @pyqtSlot()
    def on_send_click(self):
        text = self.input_area.toPlainText().strip()
        if text:
            # 启动计时和禁用按钮
            self.elapsed_seconds = 0
            self.response_timer.start(1000)
            self.status_label.setText("正在思考... 已用时：0秒")
            self.send_btn.setEnabled(False)
            self.voice_btn.setEnabled(False)
            self.file_btn.setEnabled(False)
            
            # 启动异步处理
            self._process_message(text)
            self.input_area.clear()

    def update_response_time(self):
        self.elapsed_seconds += 1
        self.status_label.setText(
            f"正在思考... 已用时：{self.elapsed_seconds}秒"
        )

    @pyqtSlot(str)
    def update_input(self, text):
        self.input_area.setPlainText(text)
        self.on_send_click()

    def _process_message(self, text):
        # if self.worker and self.worker.isRunning():
        #     self.worker.finished.disconnect()
        #     self.worker.error.disconnect()
        #     self.worker.terminate()

        prompt = f"文件上下文：{self.file_context}\n用户提问：{text}" if self.file_context else text
        print(prompt)
        # 显示用户消息
        self._append_message("👤 用户", text)
        self.worker = AIWorker(self.ai_client, prompt)
        self.worker.finished.connect(self.on_ai_response)
        self.worker.error.connect(self.on_ai_error)
        self.worker.start()

    def on_ai_response(self, response):
        """成功收到回复"""
        self.response_timer.stop()
        self._append_message("🤖 AI助手", response)
        self._restore_ui_state()
        self.file_context = None

    def on_ai_error(self, error_msg):
        """处理错误"""
        self.response_timer.stop()
        self.show_error(error_msg)
        self._restore_ui_state()

    def _restore_ui_state(self):
        """恢复界面状态"""
        self.send_btn.setEnabled(True)
        self.voice_btn.setEnabled(True)
        self.status_label.setText("就绪")

    def _append_message(self, sender: str, text: str):
        self.chat_area.append(f"""
            <div style='margin: 10px 0;'>
                <b style='color: #2c3e50;'>{sender}:</b>
                <div style='margin-left: 20px; color: #34495e;'>{text}</div>
                <hr style='border: 0.5px solid #ecf0f1;'>
            </div>
        """)
        scroll_bar = self.chat_area.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    @pyqtSlot(str)
    def show_error(self, msg):
        self.chat_area.append(f"""
            <div style='color: #e74c3c; padding: 5px;'>
                ⚠️ {msg}
            </div>
        """)
        self._restore_ui_state()

    def closeEvent(self, event):
        """窗口关闭时确保线程退出"""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            font-family: 'Microsoft YaHei', 'Segoe UI';
        }
    """)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())