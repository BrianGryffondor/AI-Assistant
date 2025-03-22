# AI 小助手 🤖

一款基于深度求索(DeepSeek)大模型的智能助手，支持语音交互和文件解析功能



## 功能特性 ✨

- **智能对话**：基于DeepSeek大模型的自然语言处理
- **多模态输入**：
  - 🎤 实时语音识别（支持中文）
  - 📁 文件解析（PDF/DOCX/TXT）
- **可视化界面**：
  - 实时响应计时
  - 消息气泡展示
  - 状态栏反馈

## 技术栈 🛠️

- **核心语言**: Python 3.10+
- **GUI框架**: PyQt5
- **语音识别**: SpeechRecognition + PyAudio
- **文件解析**: 
  - PDF: pdfplumber/PyPDF2
  - DOCX: python-docx
- **异步处理**: QThread

## 快速开始 🚀

### 环境要求
- Python 3.10+
- Windows
- 麦克风设备（语音输入功能）

### 部署步骤

1. **克隆仓库**
```
git clone https://github.com/yourusername/ai-interview-assistant.git
cd ai-interview-assistant
```
2. **安装依赖**
```
.\install.bat    
```
3. **运行**
```
.\run.bat   
```
