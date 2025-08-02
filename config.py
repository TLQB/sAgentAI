"""
Configuration file for Enhanced AI Chat Application
Tập trung tất cả cấu hình vào một file duy nhất
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()
import os

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Groq API Configuration
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Available models configuration for Groq
AVAILABLE_MODELS = {
    "Llama3-70B-8192": "llama3-70b-8192",
    "Llama3-8B-8192": "llama3-8b-8192", 
    "Mixtral-8x7B-32768": "mixtral-8x7b-32768",
    "Gemma2-9B-It": "gemma2-9b-it"
}

# Default model selection
DEFAULT_MODEL = "Llama3-70B-8192"

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

# Server configuration
SERVER_CONFIG = {
    "server_name": "0.0.0.0",
    "server_port": 7860,
    "share": True,
    "debug": True,
    "show_error": True,
    "inbrowser": True
}

# File processing configuration
FILE_PROCESSING_CONFIG = {
    "chunk_size": 100,  # Lines per chunk
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    "supported_extensions": [
        ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", 
        ".md", ".txt", ".json", ".yaml", ".yml", ".pdf"
    ]
}

# Knowledge base configuration
KNOWLEDGE_BASE_CONFIG = {
    "max_context_files": 3,
    "cache_ttl": 3600,  # 1 hour
    "max_search_results": 5
}

# Chat configuration
CHAT_CONFIG = {
    "default_temperature": 0.7,
    "default_max_tokens": 512,
    "default_streaming_speed": 0.02,
    "max_history_length": 50
}

# ============================================================================
# PATHS CONFIGURATION
# ============================================================================

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# Ensure directories exist
for directory in [KNOWLEDGE_BASE_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": os.path.join(BASE_DIR, "logs", "app.log")
}

# Ensure logs directory exists
os.makedirs(os.path.dirname(LOGGING_CONFIG["file"]), exist_ok=True)

# ============================================================================
# UI CONFIGURATION
# ============================================================================

UI_CONFIG = {
    "title": "🚀 Enhanced AI Chat with Knowledge Base",
    "description": "Chọn model Groq, upload files và bắt đầu cuộc trò chuyện thông minh!",
    "theme": "soft",
    "chatbot_height": 500,
    "max_file_count": 10
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_api_key() -> bool:
    """Validate Groq API key"""
    return bool(GROQ_API_KEY and len(GROQ_API_KEY) > 20)

def validate_model_name(model_name: str) -> bool:
    """Validate model name"""
    return model_name in AVAILABLE_MODELS.values()

def get_model_display_name(model_name: str) -> str:
    """Get display name for model"""
    for display_name, actual_name in AVAILABLE_MODELS.items():
        if actual_name == model_name:
            return display_name
    return model_name

# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================

def validate_configuration() -> Dict[str, Any]:
    """Validate all configuration settings"""
    validation_results = {
        "api_key_valid": validate_api_key(),
        "models_available": len(AVAILABLE_MODELS) > 0,
        "default_model_valid": validate_model_name(AVAILABLE_MODELS[DEFAULT_MODEL]),
        "directories_created": all(
            os.path.exists(directory) 
            for directory in [KNOWLEDGE_BASE_DIR, CACHE_DIR]
        )
    }
    
    return validation_results

# ============================================================================
# CONFIGURATION EXPORT
# ============================================================================

def get_all_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        "api": {
            "groq_api_key": GROQ_API_KEY,
            "available_models": AVAILABLE_MODELS,
            "default_model": DEFAULT_MODEL
        },
        "server": SERVER_CONFIG,
        "file_processing": FILE_PROCESSING_CONFIG,
        "knowledge_base": KNOWLEDGE_BASE_CONFIG,
        "chat": CHAT_CONFIG,
        "paths": {
            "base_dir": BASE_DIR,
            "knowledge_base_dir": KNOWLEDGE_BASE_DIR,
            "cache_dir": CACHE_DIR
        },
        "logging": LOGGING_CONFIG,
        "ui": UI_CONFIG
    } 