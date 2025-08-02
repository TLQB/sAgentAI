"""
AI Agent for Enhanced Chat Application
Tối ưu hóa AI Agent với các tính năng cần thiết
"""

import logging
from typing import Optional, Dict, Any, List
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from config import GROQ_API_KEY, CHAT_CONFIG
from .core import KnowledgeRetriever

logger = logging.getLogger(__name__)

# ============================================================================
# ENHANCED AI AGENT
# ============================================================================

class EnhancedAIAgent:
    """Enhanced AI Agent with knowledge base integration"""
    
    def __init__(self, model, tokenizer, model_name: str, knowledge_retriever: KnowledgeRetriever):
        self.model = model
        self.tokenizer = tokenizer
        self.model_name = model_name
        self.knowledge_retriever = knowledge_retriever
        
        # Generation parameters
        self.temperature = CHAT_CONFIG["default_temperature"]
        self.max_new_tokens = CHAT_CONFIG["default_max_tokens"]
        
        # Knowledge base settings
        self.kb_enabled = True
        self.max_context_files = 3
        self.debug_mode = False
        
        # Initialize memory and chain
        self._setup_memory_and_chain()
    
    def _setup_memory_and_chain(self):
        """Setup memory and LLM chain"""
        # Create prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["history", "user_input", "knowledge_context"],
            template="""
            Bạn là một trợ lý AI thông minh và hữu ích.
            
            {knowledge_context}
            
            Lịch sử trò chuyện:
            {history}
            
            Câu hỏi của người dùng: {user_input}
            
            Hướng dẫn trả lời:
            1. Trả lời bằng tiếng Việt, ngắn gọn và chính xác
            2. Sử dụng thông tin từ knowledge base nếu có
            3. Nếu không có thông tin, hãy trả lời theo sự hiểu biết của bạn
            4. Giữ giọng điệu thân thiện và chuyên nghiệp
            5. Đưa ra lời khuyên hữu ích và thực tế
            """
        )
        
        # Setup memory
        self.memory = ConversationBufferMemory(
            memory_key="history",
            input_key="user_input",
            max_token_limit=CHAT_CONFIG["max_history_length"] * 100
        )
        
        # Setup chain using RunnableSequence (new way)
        try:
            # Try new LangChain approach first
            self.chain = self.prompt_template | self.model
        except:
            # Fallback to old LLMChain if needed
            from langchain.chains import LLMChain
            self.chain = LLMChain(
                llm=self.model,
                prompt=self.prompt_template,
                memory=self.memory
            )
    
    def set_generation_params(self, temperature: float = None, max_new_tokens: int = None):
        """Set generation parameters"""
        if temperature is not None:
            self.temperature = temperature
        if max_new_tokens is not None:
            self.max_new_tokens = max_new_tokens
        
        # Update model parameters if possible
        if hasattr(self.model, 'temperature'):
            self.model.temperature = self.temperature
        if hasattr(self.model, 'max_tokens'):
            self.model.max_tokens = self.max_new_tokens
    
    def set_knowledge_base_usage(self, enabled: bool, max_context_files: int = None):
        """Set knowledge base usage"""
        self.kb_enabled = enabled
        if max_context_files is not None:
            self.max_context_files = max_context_files
    
    def set_debug_mode(self, enabled: bool):
        """Set debug mode"""
        self.debug_mode = enabled
    
    def get_model_info(self) -> str:
        """Get model information"""
        info = f"Model: {self.model_name}\n"
        info += f"Temperature: {self.temperature}\n"
        info += f"Max Tokens: {self.max_new_tokens}\n"
        info += f"Knowledge Base: {'Bật' if self.kb_enabled else 'Tắt'}\n"
        info += f"Debug Mode: {'Bật' if self.debug_mode else 'Tắt'}"
        return info
    
    def generate_response(self, user_input: str) -> str:
        """Generate response with knowledge base integration"""
        try:
            # Get knowledge context if enabled
            knowledge_context = ""
            if self.kb_enabled:
                knowledge_context = self.knowledge_retriever.retrieve_relevant_context(
                    user_input, 
                    self.max_context_files
                )
                
                if self.debug_mode:
                    logger.info(f"Knowledge context: {knowledge_context[:200]}...")
            
            # Get history safely
            try:
                history = self.memory.chat_memory.messages
            except:
                history = ""
            
            # Generate response using new or old chain approach
            try:
                # Try new RunnableSequence approach
                response = self.chain.invoke({
                    "user_input": user_input,
                    "knowledge_context": knowledge_context,
                    "history": history
                })
                return response.content if hasattr(response, 'content') else str(response)
            except:
                # Fallback to old LLMChain approach
                response = self.chain.run({
                    "user_input": user_input,
                    "knowledge_context": knowledge_context
                })
                return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"❌ Lỗi khi tạo câu trả lời: {str(e)}"
    
    def save_conversation(self, filename: str):
        """Save conversation to file"""
        try:
            # Get messages safely
            try:
                messages = self.memory.chat_memory.messages
            except:
                messages = []
            
            conversation_data = {
                "model_name": self.model_name,
                "timestamp": messages,
                "settings": {
                    "temperature": self.temperature,
                    "max_tokens": self.max_new_tokens,
                    "kb_enabled": self.kb_enabled,
                    "debug_mode": self.debug_mode
                }
            }
            
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Conversation saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")

# ============================================================================
# STREAMING CHATBOT
# ============================================================================

class StreamingChatBot:
    """Streaming chatbot with enhanced features"""
    
    def __init__(self, agent: EnhancedAIAgent):
        self.agent = agent
        self.streaming_speed = CHAT_CONFIG["default_streaming_speed"]
        self.is_generating = False
    
    def set_streaming_speed(self, speed: float):
        """Set streaming speed"""
        self.streaming_speed = speed
    
    def set_knowledge_base_enabled(self, enabled: bool):
        """Set knowledge base enabled"""
        self.agent.set_knowledge_base_usage(enabled)
    
    def stop_generation(self):
        """Stop current generation"""
        self.is_generating = False
    
    def respond_streaming(self, message: str, history: List[List[str]]):
        """Generate streaming response"""
        if not message.strip():
            yield history
            return
        
        self.is_generating = True
        
        try:
            # Add user message to history
            history.append([message, ""])
            
            # Generate response
            response = self.agent.generate_response(message)
            
            if not self.is_generating:
                return
            
            # Simulate streaming by yielding partial responses
            words = response.split()
            partial_response = ""
            
            for word in words:
                if not self.is_generating:
                    break
                
                partial_response += word + " "
                history[-1][1] = partial_response.strip()
                yield history
                
                # Simulate streaming delay
                import time
                time.sleep(self.streaming_speed)
            
            # Final response
            history[-1][1] = response
            yield history
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            history[-1][1] = f"❌ Lỗi: {str(e)}"
            yield history
        
        finally:
            self.is_generating = False

# ============================================================================
# CHATBOT MANAGER
# ============================================================================

class ChatbotManager:
    """Manage multiple chatbots"""
    
    def __init__(self):
        self.chatbots = {}
        self.current_chatbot_id = None
        self.file_processor = None
        self.knowledge_retriever = None
    
    def set_file_processor(self, file_processor):
        """Set file processor"""
        self.file_processor = file_processor
    
    def set_knowledge_retriever(self, knowledge_retriever):
        """Set knowledge retriever"""
        self.knowledge_retriever = knowledge_retriever
    
    def create_chatbot(self, model_name: str, agent: EnhancedAIAgent) -> str:
        """Create a new chatbot"""
        chatbot_id = f"chatbot_{len(self.chatbots)}_{model_name}"
        
        chatbot = StreamingChatBot(agent)
        self.chatbots[chatbot_id] = chatbot
        self.current_chatbot_id = chatbot_id
        
        logger.info(f"Created chatbot: {chatbot_id}")
        return chatbot_id
    
    def get_current_chatbot(self) -> Optional[StreamingChatBot]:
        """Get current chatbot"""
        if self.current_chatbot_id and self.current_chatbot_id in self.chatbots:
            return self.chatbots[self.current_chatbot_id]
        return None
    
    def switch_chatbot(self, chatbot_id: str) -> bool:
        """Switch to different chatbot"""
        if chatbot_id in self.chatbots:
            self.current_chatbot_id = chatbot_id
            return True
        return False
    
    def get_chatbot_list(self) -> List[Dict[str, Any]]:
        """Get list of all chatbots"""
        chatbots = []
        for chatbot_id, chatbot in self.chatbots.items():
            info = {
                "id": chatbot_id,
                "is_current": chatbot_id == self.current_chatbot_id
            }
            chatbots.append(info)
        return chatbots 