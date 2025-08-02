# 🚀 Enhanced AI Chat with Knowledge Base

Ứng dụng chat AI nâng cao với knowledge base, sử dụng Groq Cloud API cho tốc độ xử lý cực nhanh.

## ✨ Tính năng chính

### 🤖 **AI Chat thông minh**
- Hỗ trợ nhiều model Groq (Llama3-70B, Mixtral-8x7B, Gemma2-9B)
- Streaming response với tốc độ tùy chỉnh
- Memory conversation để duy trì context
- Debug mode để theo dõi quá trình xử lý

### 📚 **Knowledge Base Management**
- Upload và xử lý nhiều loại file (PDF, Python, JavaScript, Markdown, etc.)
- Chia file thành chunks nhỏ để tối ưu tìm kiếm
- Tìm kiếm semantic và keyword
- Cache thông minh để tăng tốc độ

### ⚙️ **Cài đặt linh hoạt**
- Điều chỉnh temperature và max tokens
- Bật/tắt knowledge base
- Tùy chỉnh streaming speed
- Debug mode cho developers

## 🏗️ Kiến trúc tối ưu hóa

```
📁 Enhanced AI Chat/
├── 📄 app.py                 # Main application
├── 📄 config.py              # Centralized configuration
├── 📁 utils/
│   ├── 📄 core.py            # Core functionality
│   └── 📄 ai_agent.py        # AI Agent & Chatbot
├── 📁 knowledge_base/        # Processed files
├── 📁 cache/                 # Cache storage
└── 📁 logs/                  # Application logs
```

## 🚀 Cài đặt và chạy

### 1. **Clone repository**
```bash
git clone <repository-url>
cd Enhanced-AI-Chat
```

### 2. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Cấu hình API Key**
Chỉnh sửa `config.py`:
```python
GROQ_API_KEY = "your_groq_api_key_here"
```

### 4. **Chạy ứng dụng**
```bash
python app.py
```

Ứng dụng sẽ chạy tại: `http://localhost:7860`

## 📊 So sánh hiệu suất

| Tiêu chí | Trước tối ưu | Sau tối ưu |
|----------|-------------|------------|
| **Số file** | 25+ files | 3 core files |
| **Dependencies** | 15+ packages | 5 core packages |
| **Code lines** | 3000+ lines | 800+ lines |
| **Startup time** | 10-15s | 2-3s |
| **Memory usage** | 500MB+ | 100MB+ |
| **Maintainability** | Khó | Dễ |

## 🎯 Cách sử dụng

### **1. Load Model**
- Chọn model Groq từ dropdown
- Click "Load Model"
- Kiểm tra thông tin model

### **2. Upload Files**
- Mở "Knowledge Base Management"
- Upload files (PDF, Python, JS, MD, TXT, etc.)
- Click "Process Files"
- Theo dõi trạng thái xử lý

### **3. Chat với AI**
- Nhập câu hỏi
- AI sẽ tìm kiếm trong knowledge base
- Trả lời dựa trên thông tin có sẵn

### **4. Tìm kiếm Knowledge Base**
- Sử dụng search box
- Tìm kiếm thông tin cụ thể
- Xem kết quả chi tiết

## ⚙️ Cấu hình nâng cao

### **File Processing**
```python
FILE_PROCESSING_CONFIG = {
    "chunk_size": 100,           # Lines per chunk
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    "supported_extensions": [".py", ".js", ".md", ...]
}
```

### **Knowledge Base**
```python
KNOWLEDGE_BASE_CONFIG = {
    "max_context_files": 3,      # Max files per query
    "cache_ttl": 3600,          # Cache timeout (1 hour)
    "max_search_results": 5     # Max search results
}
```

### **Chat Settings**
```python
CHAT_CONFIG = {
    "default_temperature": 0.7,
    "default_max_tokens": 512,
    "default_streaming_speed": 0.02,
    "max_history_length": 50
}
```

## 🔧 Tùy chỉnh

### **Thêm model mới**
Chỉnh sửa `config.py`:
```python
AVAILABLE_MODELS = {
    "Your-Model": "your-model-name",
    # ... existing models
}
```

### **Thêm file type**
```python
FILE_PROCESSING_CONFIG["supported_extensions"].append(".your_extension")
```

### **Tùy chỉnh prompt**
Chỉnh sửa `utils/ai_agent.py`:
```python
self.prompt_template = PromptTemplate(
    input_variables=["history", "user_input", "knowledge_context"],
    template="Your custom prompt template here..."
)
```

## 🐛 Troubleshooting

### **Lỗi API Key**
```
❌ Error loading model: Invalid API key
```
**Giải pháp:** Kiểm tra `GROQ_API_KEY` trong `config.py`

### **Lỗi file upload**
```
❌ File không tồn tại
```
**Giải pháp:** Kiểm tra đường dẫn file và quyền truy cập

### **Lỗi memory**
```
❌ Out of memory
```
**Giải pháp:** Giảm `chunk_size` trong `config.py`

## 📈 Performance Tips

### **Tối ưu tốc độ**
1. Sử dụng cache (mặc định bật)
2. Giảm `max_context_files`
3. Tắt debug mode khi không cần

### **Tối ưu memory**
1. Giảm `chunk_size`
2. Giới hạn `max_history_length`
3. Xóa files không cần thiết

### **Tối ưu accuracy**
1. Tăng `max_search_results`
2. Bật debug mode để kiểm tra
3. Sử dụng keywords cụ thể

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## 🙏 Acknowledgments

- **Groq** - Cloud API cho inference nhanh
- **Gradio** - UI framework
- **LangChain** - LLM framework

---

**Made with ❤️ for the AI community** 