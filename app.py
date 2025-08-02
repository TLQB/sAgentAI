# -*- coding: utf-8 -*-
"""
Enhanced AI Chat Application
Ứng dụng chat AI nâng cao với knowledge base
"""

import gradio as gr
import time
import os
from typing import Optional, List, Dict, Any
import logging

# Import configuration
from config import (
    AVAILABLE_MODELS, DEFAULT_MODEL, GROQ_API_KEY,
    SERVER_CONFIG, UI_CONFIG, FILE_PROCESSING_CONFIG
)

# Import core modules
from utils.core import FileProcessor, KnowledgeRetriever, StatusTracker, setup_logging
from utils.ai_agent import EnhancedAIAgent, StreamingChatBot, ChatbotManager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# ============================================================================
# MODEL LOADING
# ============================================================================

def load_model(model_name: str):
    """Load Groq model with error handling"""
    try:
        logger.info(f"Loading Groq model: {model_name}")
        
        from langchain_groq import ChatGroq
        
        model = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name=model_name
        )
        
        logger.info(f"Successfully loaded model: {model_name}")
        return model, None
        
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {e}")
        
        # Fallback to default model
        try:
            logger.info("Trying fallback model...")
            model = ChatGroq(
                groq_api_key=GROQ_API_KEY,
                model_name=AVAILABLE_MODELS[DEFAULT_MODEL]
            )
            logger.info("Fallback model loaded successfully")
            return model, None
            
        except Exception as e2:
            logger.error(f"Error loading fallback model: {e2}")
            return None, None

# ============================================================================
# APPLICATION MANAGER
# ============================================================================

class ApplicationManager:
    """Main application manager"""
    
    def __init__(self):
        # Initialize core components
        self.file_processor = FileProcessor()
        self.knowledge_retriever = KnowledgeRetriever(self.file_processor)
        self.status_tracker = StatusTracker()
        self.chatbot_manager = ChatbotManager()
        
        # Setup chatbot manager
        self.chatbot_manager.set_file_processor(self.file_processor)
        self.chatbot_manager.set_knowledge_retriever(self.knowledge_retriever)
        
        # Current model and agent
        self.current_model = None
        self.current_agent = None
        self.current_chatbot = None
    
    def load_model(self, model_key: str) -> bool:
        """Load model and create agent"""
        try:
            model_name = AVAILABLE_MODELS.get(model_key)
            if not model_name:
                logger.error(f"Model {model_key} not found")
                return False
            
            # Load model
            model, tokenizer = load_model(model_name)
            if model is None:
                return False
            
            # Create agent
            self.current_model = model
            self.current_agent = EnhancedAIAgent(
                model, tokenizer, model_key, self.knowledge_retriever
            )
            
            # Create chatbot
            chatbot_id = self.chatbot_manager.create_chatbot(model_key, self.current_agent)
            self.current_chatbot = self.chatbot_manager.get_current_chatbot()
            
            logger.info(f"Successfully loaded model {model_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def process_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Process files for knowledge base"""
        try:
            self.status_tracker.start_processing(f"Processing {len(file_paths)} files...")
            
            results = []
            for i, file_path in enumerate(file_paths):
                progress = (i / len(file_paths)) * 90
                self.status_tracker.update_progress(progress, f"Processing file {i+1}/{len(file_paths)}")
                
                result = self.file_processor.process_file(file_path)
                if result.get("success"):
                    total_chunks = result.get('total_chunks', 0)
                    results.append(f"✅ {file_path}: {total_chunks} chunks")
                else:
                    results.append(f"❌ {file_path}: {result.get('error', 'Unknown error')}")
            
            self.status_tracker.success(f"Processed {len(file_paths)} files successfully")
            return {"success": True, "results": results}
            
        except Exception as e:
            error_msg = f"Error processing files: {str(e)}"
            self.status_tracker.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_knowledge_base_status(self) -> Dict[str, Any]:
        """Get knowledge base status"""
        try:
            total_files = len(self.file_processor.file_index)
            total_chunks = 0
            
            for file_info in self.file_processor.file_index.values():
                if "chunks" in file_info:
                    total_chunks += len(file_info["chunks"])
                else:
                    total_chunks += 1
            
            return {
                "total_files": total_files,
                "total_chunks": total_chunks,
                "status": "✅ Knowledge Base ready" if total_files > 0 else "❌ No files"
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_files": 0,
                "total_chunks": 0,
                "status": "❌ Error checking Knowledge Base"
            }
    
    def search_knowledge_base(self, query: str) -> str:
        """Search knowledge base"""
        return self.knowledge_retriever.retrieve_relevant_context(query)
    
    def get_current_agent(self) -> Optional[EnhancedAIAgent]:
        return self.current_agent
    
    def get_current_chatbot(self) -> Optional[StreamingChatBot]:
        return self.current_chatbot

# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_chat_interface():
    """Create the main chat interface"""
    
    # Initialize application manager
    app_manager = ApplicationManager()
    
    # Load default model
    app_manager.load_model(DEFAULT_MODEL)
    
    with gr.Blocks(title=UI_CONFIG["title"], theme=gr.themes.Soft()) as demo:
        
        # Header
        gr.Markdown(f"# {UI_CONFIG['title']}")
        gr.Markdown(f"### {UI_CONFIG['description']}")
        
        # Model selection
        with gr.Row():
            with gr.Column(scale=2):
                model_dropdown = gr.Dropdown(
                    choices=list(AVAILABLE_MODELS.keys()),
                    value=DEFAULT_MODEL,
                    label="Select Groq Model"
                )
                load_model_btn = gr.Button("🔄 Load Model", variant="primary")
            
            with gr.Column(scale=1):
                model_info = gr.Textbox(
                    label="Model Information",
                    value="Model not loaded",
                    interactive=False
                )
        
        # Knowledge Base Management
        with gr.Accordion("📚 Knowledge Base Management", open=False):
            with gr.Row():
                with gr.Column(scale=2):
                    file_upload = gr.File(
                        label="Upload Files (PDF, Python, JS, MD, TXT, etc.)",
                        file_count="multiple",
                        file_types=FILE_PROCESSING_CONFIG["supported_extensions"]
                    )
                    
                    with gr.Row():
                        process_files_btn = gr.Button("📥 Process Files", variant="primary")
                        reload_kb_btn = gr.Button("🔄 Reload Knowledge Base", variant="secondary")
                    
                    processing_status = gr.Textbox(
                        label="Processing Status",
                        value="Ready",
                        interactive=False
                    )
                
                with gr.Column(scale=1):
                    kb_status = gr.Textbox(
                        label="Knowledge Base Status",
                        value="No files",
                        interactive=False
                    )
            
            with gr.Row():
                with gr.Column():
                    kb_search_input = gr.Textbox(
                        label="Search Knowledge Base",
                        placeholder="Enter keywords to search...",
                        lines=2
                    )
                    kb_search_btn = gr.Button("🔍 Search", variant="secondary")
                
                with gr.Column():
                    kb_search_result = gr.Textbox(
                        label="Search Results",
                        lines=8,
                        interactive=False
                    )
        
        # Chat interface
        chatbot_ui = gr.Chatbot(
            label="Conversation",
            height=UI_CONFIG["chatbot_height"],
            show_copy_button=True,
            avatar_images=("👤", "🤖")
        )
        
        # Input controls
        with gr.Row():
            msg_input = gr.Textbox(
                label="Your Message",
                placeholder="Enter your question...",
                lines=2,
                scale=4
            )
            with gr.Column(scale=1):
                send_btn = gr.Button("📤 Send", variant="primary")
                stop_btn = gr.Button("⏹️ Stop", variant="stop")
        
        # Control buttons
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear History", variant="secondary")
            retry_btn = gr.Button("🔄 Retry", variant="secondary")
            save_btn = gr.Button("💾 Save Conversation", variant="secondary")
        
        # Settings
        with gr.Accordion("⚙️ Advanced Settings", open=False):
            with gr.Row():
                with gr.Column():
                    temperature_slider = gr.Slider(
                        minimum=0.1, maximum=1.0, value=0.7, step=0.1,
                        label="Temperature"
                    )
                    max_tokens_slider = gr.Slider(
                        minimum=100, maximum=1000, value=512, step=50,
                        label="Max Tokens"
                    )
                
                with gr.Column():
                    streaming_speed_slider = gr.Slider(
                        minimum=0.01, maximum=0.1, value=0.02, step=0.01,
                        label="Streaming Speed"
                    )
                    kb_enabled_checkbox = gr.Checkbox(
                        value=True,
                        label="Use Knowledge Base"
                    )
                    debug_mode_checkbox = gr.Checkbox(
                        value=False,
                        label="Debug Mode"
                    )
        
        # Examples
        gr.Examples(
            examples=[
                "Hello! Can you introduce yourself?",
                "Tell me a short story",
                "Explain artificial intelligence",
                "Write a poem about nature",
                "Can you help me write Python code?",
                "Goodbye!"
            ],
            inputs=msg_input
        )
        
        # Event handlers
        def load_model_handler(model_key):
            success = app_manager.load_model(model_key)
            if success:
                agent = app_manager.get_current_agent()
                info = agent.get_model_info() if agent else "No information"
                return f"✅ Model {model_key} loaded successfully!\n{info}"
            else:
                return "❌ Error loading model"
        
        def process_files_handler(files):
            if not files:
                return "❌ No files selected", "No files"
            
            try:
                file_paths = [file.name for file in files]
                result = app_manager.process_files(file_paths)
                
                if result.get("success"):
                    results_text = "\n".join(result.get("results", []))
                    status = app_manager.get_knowledge_base_status()
                    status_text = status.get("status", "Unknown")
                    return results_text, status_text
                else:
                    return f"❌ Error: {result.get('error', 'Unknown error')}", "No files"
                    
            except Exception as e:
                return f"❌ Error: {str(e)}", "No files"
        
        def search_kb_handler(query):
            if not query.strip():
                return "❌ Please enter search keywords"
            
            result = app_manager.search_knowledge_base(query)
            return result
        
        def handle_streaming_message(message, history):
            chatbot = app_manager.get_current_chatbot()
            if chatbot:
                yield from chatbot.respond_streaming(message, history)
            else:
                history.append([message, "❌ Model not loaded"])
                yield history
        
        def update_settings(temperature, max_tokens, streaming_speed, kb_enabled, debug_mode):
            agent = app_manager.get_current_agent()
            chatbot = app_manager.get_current_chatbot()
            
            if agent:
                agent.set_generation_params(temperature, int(max_tokens))
                agent.set_knowledge_base_usage(kb_enabled)
                agent.set_debug_mode(debug_mode)
            
            if chatbot:
                chatbot.set_streaming_speed(streaming_speed)
                chatbot.set_knowledge_base_enabled(kb_enabled)
            
            return "✅ Settings updated"
        
        def save_conversation():
            agent = app_manager.get_current_agent()
            if agent:
                filename = f"conversation_{time.strftime('%Y%m%d_%H%M%S')}.json"
                agent.save_conversation(filename)
                return f"✅ Conversation saved to {filename}"
            return "❌ No agent to save"
        
        def retry_last_message(history):
            if history:
                last_user_message = history[-1][0]
                history = history[:-1]
                chatbot = app_manager.get_current_chatbot()
                if chatbot:
                    yield from chatbot.respond_streaming(last_user_message, history)
                else:
                    history.append([last_user_message, "❌ Model not loaded"])
                    yield history
        
        def reload_knowledge_base():
            try:
                app_manager.file_processor.load_file_index()
                status = app_manager.get_knowledge_base_status()
                return status.get("status", "Unknown")
            except Exception as e:
                return f"❌ Error reloading Knowledge Base: {str(e)}"
        
        # Connect events
        load_model_btn.click(
            load_model_handler,
            inputs=[model_dropdown],
            outputs=[model_info]
        )
        
        process_files_btn.click(
            process_files_handler,
            inputs=[file_upload],
            outputs=[gr.Textbox(label="Processing Results"), kb_status]
        )
        
        reload_kb_btn.click(
            reload_knowledge_base,
            outputs=[kb_status]
        )
        
        kb_search_btn.click(
            search_kb_handler,
            inputs=[kb_search_input],
            outputs=[kb_search_result]
        )
        
        send_event = send_btn.click(
            handle_streaming_message,
            inputs=[msg_input, chatbot_ui],
            outputs=[chatbot_ui]
        ).then(lambda: "", outputs=[msg_input])
        
        submit_event = msg_input.submit(
            handle_streaming_message,
            inputs=[msg_input, chatbot_ui],
            outputs=[chatbot_ui]
        ).then(lambda: "", outputs=[msg_input])
        
        stop_btn.click(
            lambda: app_manager.get_current_chatbot().stop_generation() if app_manager.get_current_chatbot() else None,
            cancels=[send_event, submit_event]
        )
        
        clear_btn.click(lambda: [], outputs=[chatbot_ui])
        
        retry_btn.click(
            retry_last_message,
            inputs=[chatbot_ui],
            outputs=[chatbot_ui]
        )
        
    return demo

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting Enhanced AI Chat Application...")
    logger.info("Using Groq Cloud API for fast inference!")
    
    # Create and launch interface
    demo = create_chat_interface()
    
    # Launch with optimal configuration
    demo.launch(**SERVER_CONFIG) 