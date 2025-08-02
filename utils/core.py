"""
Core utilities for Enhanced AI Chat Application
Tập trung các chức năng cốt lõi vào một module duy nhất
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Import configuration
from config import (
    KNOWLEDGE_BASE_DIR, 
    CACHE_DIR,
    FILE_PROCESSING_CONFIG,
    KNOWLEDGE_BASE_CONFIG
)

logger = logging.getLogger(__name__)

# ============================================================================
# FILE PROCESSING CORE
# ============================================================================

class FileProcessor:
    """Core file processing functionality"""
    
    def __init__(self):
        self.file_index = {}
        self.index_file = os.path.join(KNOWLEDGE_BASE_DIR, "file_index.json")
        self.load_file_index()
    
    def load_file_index(self):
        """Load file index from disk"""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.file_index = json.load(f)
                logger.info(f"Loaded {len(self.file_index)} files from index")
        except Exception as e:
            logger.error(f"Error loading file index: {e}")
            self.file_index = {}
    
    def save_file_index(self):
        """Save file index to disk"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving file index: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Get file hash for change detection"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error getting file hash: {e}")
            return ""
    
    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content with encoding detection"""
        try:
            file_path = Path(file_path)
            
            # Handle PDF files
            if file_path.suffix.lower() == '.pdf':
                return self._read_pdf_content(str(file_path))
            
            # Handle text files
            encodings = ['utf-8', 'latin-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            logger.error(f"Could not read file with any encoding: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return None
    
    def _read_pdf_content(self, file_path: str) -> Optional[str]:
        """Read PDF file content"""
        try:
            # Try to import PyPDF2 or pypdf
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                try:
                    import pypdf
                    with open(file_path, 'rb') as file:
                        pdf_reader = pypdf.PdfReader(file)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    logger.warning("PDF libraries not installed. Install with: pip install PyPDF2")
                    return f"[PDF file: {Path(file_path).name} - PDF processing not available]"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return None
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {"error": f"File không tồn tại: {file_path}"}
            
            # Check if file is already processed and unchanged
            current_hash = self.get_file_hash(str(file_path))
            if str(file_path) in self.file_index:
                stored_hash = self.file_index[str(file_path)].get("file_hash", "")
                if current_hash == stored_hash:
                    return {"success": True, "message": "File unchanged"}
            
            # Read and process file
            content = self.read_file_content(str(file_path))
            if not content:
                return {"error": f"Không thể đọc file: {file_path}"}
            
            # Create chunks
            chunks = self._split_content_into_chunks(content)
            
            # Save file info
            file_info = {
                "name": file_path.name,
                "path": str(file_path),
                "size": len(content),
                "total_chunks": len(chunks),
                "chunks": chunks,
                "processed_at": datetime.now().isoformat(),
                "file_hash": current_hash
            }
            
            self.file_index[str(file_path)] = file_info
            self.save_file_index()
            
            return {
                "success": True,
                "file_name": file_path.name,
                "total_chunks": len(chunks),
                "total_size": len(content)
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {"error": str(e)}
    
    def _split_content_into_chunks(self, content: str, chunk_size: int = None) -> Dict[str, Any]:
        """Split content into chunks"""
        if chunk_size is None:
            chunk_size = FILE_PROCESSING_CONFIG["chunk_size"]
        
        lines = content.split('\n')
        chunks = {}
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            chunk_id = f"chunk_{i // chunk_size}"
            
            chunks[chunk_id] = {
                "content": chunk_content,
                "start_line": i + 1,
                "end_line": min(i + chunk_size, len(lines)),
                "keywords": self._extract_keywords(chunk_content),
                "summary": self._generate_chunk_summary(chunk_content)
            }
        
        return chunks
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction - can be enhanced
        words = content.lower().split()
        # Remove common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(keywords))[:10]  # Top 10 keywords
    
    def _generate_chunk_summary(self, content: str) -> str:
        """Generate summary for chunk"""
        # Simple summary - can be enhanced with AI
        lines = content.split('\n')
        if len(lines) <= 3:
            return content[:200] + "..." if len(content) > 200 else content
        return lines[0][:100] + "..." if len(lines[0]) > 100 else lines[0]

# ============================================================================
# KNOWLEDGE RETRIEVER CORE
# ============================================================================

class KnowledgeRetriever:
    """Core knowledge retrieval functionality"""
    
    def __init__(self, file_processor: FileProcessor):
        self.file_processor = file_processor
        self.cache = {}
        self.cache_ttl = KNOWLEDGE_BASE_CONFIG["cache_ttl"]
        self.last_cache_cleanup = time.time()
    
    def retrieve_relevant_context(self, query: str, max_files: int = None) -> str:
        """Retrieve relevant context for query"""
        if max_files is None:
            max_files = KNOWLEDGE_BASE_CONFIG["max_context_files"]
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(query, max_files)
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if time.time() - cache_entry.get("timestamp", 0) < self.cache_ttl:
                    return cache_entry["result"]
            
            # Search for relevant content
            relevant_chunks = self._search_content(query, max_files)
            
            if not relevant_chunks:
                return "Không tìm thấy thông tin liên quan."
            
            # Format results
            result = self._format_search_results(relevant_chunks)
            
            # Cache result
            self.cache[cache_key] = {
                "result": result,
                "timestamp": time.time()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return "Có lỗi xảy ra khi tìm kiếm thông tin."
    
    def _get_cache_key(self, query: str, max_files: int) -> str:
        """Generate cache key"""
        cache_data = {
            "query": query,
            "max_files": max_files,
            "file_count": len(self.file_processor.file_index)
        }
        return hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
    
    def _search_content(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search for relevant content"""
        query_terms = query.lower().split()
        results = []
        
        for file_path, file_info in self.file_processor.file_index.items():
            if "chunks" not in file_info:
                continue
            
            for chunk_id, chunk_info in file_info["chunks"].items():
                relevance_score = self._calculate_relevance(query_terms, chunk_info)
                
                if relevance_score > 0:
                    results.append({
                        "file_name": file_info["name"],
                        "file_path": file_path,
                        "chunk_id": chunk_id,
                        "content": chunk_info["content"],
                        "relevance_score": relevance_score
                    })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:max_results]
    
    def _calculate_relevance(self, query_terms: List[str], chunk_info: Dict[str, Any]) -> float:
        """Calculate relevance score"""
        content = chunk_info["content"].lower()
        keywords = [kw.lower() for kw in chunk_info.get("keywords", [])]
        
        score = 0.0
        
        # Exact term matches
        for term in query_terms:
            if term in content:
                score += 2.0
            if term in keywords:
                score += 1.5
        
        # Partial matches
        for term in query_terms:
            for keyword in keywords:
                if term in keyword or keyword in term:
                    score += 0.5
        
        return score
    
    def _format_search_results(self, chunks: List[Dict[str, Any]]) -> str:
        """Format search results"""
        if not chunks:
            return "Không tìm thấy thông tin liên quan."
        
        result_parts = []
        for chunk in chunks:
            result_parts.append(f"📄 {chunk['file_name']}:\n{chunk['content'][:500]}...")
        
        return "\n\n".join(result_parts)

# ============================================================================
# STATUS TRACKER CORE
# ============================================================================

class StatusTracker:
    """Core status tracking functionality"""
    
    def __init__(self):
        self.current_status = "Sẵn sàng"
        self.progress = 0
        self.start_time = None
        self.last_update = None
    
    def start_processing(self, status: str):
        """Start processing with status"""
        self.current_status = status
        self.progress = 0
        self.start_time = time.time()
        self.last_update = time.time()
        logger.info(f"Started processing: {status}")
    
    def update_progress(self, progress: float, status: str = None):
        """Update progress"""
        self.progress = min(100, max(0, progress))
        if status:
            self.current_status = status
        self.last_update = time.time()
    
    def success(self, message: str):
        """Mark as successful"""
        self.current_status = f"✅ {message}"
        self.progress = 100
        self.last_update = time.time()
        logger.info(f"Success: {message}")
    
    def error(self, message: str):
        """Mark as error"""
        self.current_status = f"❌ {message}"
        self.last_update = time.time()
        logger.error(f"Error: {message}")
    
    def get_status_text(self) -> str:
        """Get current status text"""
        if self.start_time and self.last_update:
            elapsed = self.last_update - self.start_time
            return f"{self.current_status} ({elapsed:.1f}s)"
        return self.current_status
    
    def get_progress(self) -> float:
        """Get current progress"""
        return self.progress

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_logging():
    """Setup logging configuration"""
    from config import LOGGING_CONFIG
    
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG["level"]),
        format=LOGGING_CONFIG["format"],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG["file"]),
            logging.StreamHandler()
        ]
    )

def validate_file_extension(filename: str) -> bool:
    """Validate file extension"""
    ext = Path(filename).suffix.lower()
    return ext in FILE_PROCESSING_CONFIG["supported_extensions"]

def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except:
        return 0.0 