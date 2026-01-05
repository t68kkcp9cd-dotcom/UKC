"""
Ollama client for local AI model integration
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator

from app.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def connect(self):
        """Establish connection to Ollama"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                base_url=self.base_url,
                timeout=aiohttp.ClientTimeout(total=settings.OLLAMA_TIMEOUT)
            )
            
    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            self.session = None
            
    async def _ensure_session(self):
        """Ensure session is created"""
        if self.session is None or self.session.closed:
            await self.connect()
            
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            await self._ensure_session()
            
            async with self.session.get("/api/tags") as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
            
    async def list_models(self) -> Dict[str, Any]:
        """List available models"""
        try:
            await self._ensure_session()
            
            async with self.session.get("/api/tags") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to list models: {response.status}")
                    
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise
            
    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama"""
        try:
            await self._ensure_session()
            
            async with self.session.post(
                "/api/pull",
                json={"name": model_name}
            ) as response:
                if response.status == 200:
                    # Read the streaming response
                    async for line in response.content:
                        if line:
                            data = json.loads(line.decode())
                            if data.get("status") == "success":
                                logger.info(f"Model {model_name} pulled successfully")
                                return True
                    return False
                else:
                    raise Exception(f"Failed to pull model: {response.status}")
                    
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            raise
            
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[List[int]] = None,
        stream: bool = False,
        raw: bool = False,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        keep_alive: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate text completion"""
        try:
            await self._ensure_session()
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            
            # Add optional parameters
            if system:
                payload["system"] = system
            if template:
                payload["template"] = template
            if context:
                payload["context"] = context
            if raw:
                payload["raw"] = raw
            if format:
                payload["format"] = format
            if options:
                payload["options"] = options
            if keep_alive:
                payload["keep_alive"] = keep_alive
                
            async with self.session.post("/api/generate", json=payload) as response:
                if response.status == 200:
                    if stream:
                        # Handle streaming response
                        result = {"response": "", "context": None}
                        async for line in response.content:
                            if line:
                                data = json.loads(line.decode())
                                if "response" in data:
                                    result["response"] += data["response"]
                                if "context" in data:
                                    result["context"] = data["context"]
                        return result
                    else:
                        return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Generation failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
            
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        format: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
        keep_alive: Optional[str] = None
    ) -> Dict[str, Any]:
        """Chat completion with conversation history"""
        try:
            await self._ensure_session()
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": stream
            }
            
            # Add optional parameters
            if format:
                payload["format"] = format
            if options:
                payload["options"] = options
            if keep_alive:
                payload["keep_alive"] = keep_alive
                
            async with self.session.post("/api/chat", json=payload) as response:
                if response.status == 200:
                    if stream:
                        # Handle streaming response
                        result = {"message": {"role": "assistant", "content": ""}}
                        async for line in response.content:
                            if line:
                                data = json.loads(line.decode())
                                if "message" in data and "content" in data["message"]:
                                    result["message"]["content"] += data["message"]["content"]
                        return result
                    else:
                        return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Chat failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise
            
    async def embeddings(self, model: str, prompt: str) -> Dict[str, Any]:
        """Generate embeddings for text"""
        try:
            await self._ensure_session()
            
            payload = {
                "model": model,
                "prompt": prompt
            }
            
            async with self.session.post("/api/embeddings", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Embeddings failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Embeddings failed: {e}")
            raise
            
    async def create_model(
        self,
        name: str,
        modelfile: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Create a new model from Modelfile"""
        try:
            await self._ensure_session()
            
            payload = {
                "name": name,
                "modelfile": modelfile,
                "stream": stream
            }
            
            async with self.session.post("/api/create", json=payload) as response:
                if response.status == 200:
                    if stream:
                        # Handle streaming response
                        result = {"status": "success"}
                        async for line in response.content:
                            if line:
                                data = json.loads(line.decode())
                                if "error" in data:
                                    raise Exception(data["error"])
                        return result
                    else:
                        return await response.json()
                else:
                    raise Exception(f"Model creation failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Model creation failed: {e}")
            raise
            
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model"""
        try:
            await self._ensure_session()
            
            async with self.session.delete(f"/api/delete", json={"name": model_name}) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Model deletion failed: {e}")
            raise
            
    async def copy_model(self, source: str, destination: str) -> bool:
        """Copy a model"""
        try:
            await self._ensure_session()
            
            payload = {
                "source": source,
                "destination": destination
            }
            
            async with self.session.post("/api/copy", json=payload) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Model copy failed: {e}")
            raise
            
    async def show_model(self, model_name: str) -> Dict[str, Any]:
        """Show model information"""
        try:
            await self._ensure_session()
            
            async with self.session.post("/api/show", json={"name": model_name}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Show model failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Show model failed: {e}")
            raise
            
    async def get_ps_info(self) -> Dict[str, Any]:
        """Get running processes information"""
        try:
            await self._ensure_session()
            
            async with self.session.get("/api/ps") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Get processes failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Get processes failed: {e}")
            raise