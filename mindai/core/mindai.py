"""
Main MindAI Class - Core orchestrator for the AI agent system
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from mindai.core.memory import MemoryGraph, MemoryNode, NodeType, RelationshipType
from mindai.core.storage import Storage
from mindai.core.llm import LLMClient, LLMProvider, LLMMessage
from mindai.skills import SkillRegistry, BaseSkill


class MindAI:
    """Main MindAI agent class"""
    
    def __init__(
        self,
        data_dir: Optional[str] = None,
        llm_provider: LLMProvider = LLMProvider.OPENAI,
        llm_model: Optional[str] = None,
        llm_api_key: Optional[str] = None,
    ):
        self.storage = Storage(data_dir)
        self.memory = MemoryGraph()
        self.skill_registry = SkillRegistry()
        self.llm_client = None  # Lazy initialization
        
        # Configuration
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_api_key = llm_api_key
        self.initialized = False
    
    async def initialize(self):
        """Initialize MindAI (load memory, skills, etc.)"""
        if self.initialized:
            return
        
        # Initialize storage
        await self.storage.initialize()
        
        # Load memory graph
        self.memory = await self.storage.load_memory_graph()
        
        # Initialize LLM client
        config = self.storage.load_config()
        provider = config.get("llm_provider", self.llm_provider.value)
        model = config.get("llm_model", self.llm_model)
        api_key = config.get("llm_api_key", self.llm_api_key)
        
        try:
            self.llm_client = LLMClient(
                provider=LLMProvider(provider),
                model=model,
                api_key=api_key,
            )
        except (ValueError, ImportError) as e:
            print(f"Warning: LLM client initialization failed: {e}")
            print("You can set LLM configuration later using set_llm_config()")
        
        # Load skills
        await self.skill_registry.load_skills()
        
        self.initialized = True
    
    def set_llm_config(
        self,
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Update LLM configuration"""
        config = self.storage.load_config()
        
        if provider:
            config["llm_provider"] = provider.value
            self.llm_provider = provider
        if model:
            config["llm_model"] = model
            self.llm_model = model
        if api_key:
            config["llm_api_key"] = api_key
            self.llm_api_key = api_key
        
        self.storage.save_config(config)
        
        # Reinitialize LLM client
        try:
            self.llm_client = LLMClient(
                provider=self.llm_provider,
                model=self.llm_model,
                api_key=self.llm_api_key,
            )
        except (ValueError, ImportError) as e:
            raise ValueError(f"Failed to initialize LLM client: {e}")
    
    async def process(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a user query and execute appropriate actions"""
        if not self.initialized:
            await self.initialize()
        
        if not self.llm_client:
            raise ValueError("LLM client not initialized. Please set LLM configuration.")
        
        # Get relevant context from memory
        context_nodes = self.memory.get_context(query, max_nodes=20)
        context_strings = [node.content for node in context_nodes]
        
        # Get available skills
        available_skills = [
            {
                "name": skill.name,
                "description": skill.description,
                "parameters": skill.get_parameters(),
            }
            for skill in self.skill_registry.get_enabled_skills()
        ]
        
        # Reason about the query
        reasoning_result = self.llm_client.reason(
            query=query,
            context=context_strings,
            available_skills=available_skills,
        )
        
        # Execute skills
        execution_results = []
        for skill_info in reasoning_result.get("skills", []):
            skill_name = skill_info["name"]
            skill_params = skill_info.get("params", {})
            
            skill = self.skill_registry.get_skill(skill_name)
            if not skill:
                execution_results.append({
                    "skill": skill_name,
                    "status": "error",
                    "error": f"Skill '{skill_name}' not found",
                })
                continue
            
            try:
                # Execute skill
                result = await skill.execute(
                    context={
                        "query": query,
                        "memory": self.memory,
                        "user_id": user_id,
                    },
                    params=skill_params,
                )
                
                execution_results.append({
                    "skill": skill_name,
                    "status": "success",
                    "result": result,
                })
                
                # Log execution
                execution_id = str(uuid.uuid4())
                await self.storage.log_execution(
                    execution_id=execution_id,
                    skill_id=skill_name,
                    input_data=skill_params,
                    output_data=result,
                    status="success",
                )
                
                # Update memory with execution result
                self._update_memory_from_execution(query, skill_name, result)
                
            except Exception as e:
                execution_results.append({
                    "skill": skill_name,
                    "status": "error",
                    "error": str(e),
                })
                
                # Log error
                execution_id = str(uuid.uuid4())
                await self.storage.log_execution(
                    execution_id=execution_id,
                    skill_id=skill_name,
                    input_data=skill_params,
                    output_data=None,
                    status="error",
                    error_message=str(e),
                )
        
        # Save memory graph
        await self.storage.save_memory_graph(self.memory)
        
        return {
            "query": query,
            "reasoning": reasoning_result.get("reasoning", ""),
            "intent": reasoning_result.get("intent", ""),
            "response": reasoning_result.get("response", ""),
            "executions": execution_results,
        }
    
    def _update_memory_from_execution(
        self,
        query: str,
        skill_name: str,
        result: Dict[str, Any],
    ):
        """Update memory graph based on skill execution"""
        # Create a node for this interaction
        interaction_id = f"interaction_{datetime.now().timestamp()}"
        interaction_node = MemoryNode(
            id=interaction_id,
            type=NodeType.EVENT,
            content=f"User query: {query}\nSkill executed: {skill_name}\nResult: {result}",
            metadata={
                "skill": skill_name,
                "result": result,
            },
            importance=0.6,
        )
        self.memory.add_node(interaction_node)
        
        # Try to link to related nodes from the query context
        context_nodes = self.memory.get_context(query, max_nodes=5)
        for node in context_nodes:
            self.memory.add_edge(
                node.id,
                interaction_id,
                RelationshipType.RELATED_TO,
            )
    
    async def add_memory(
        self,
        content: str,
        node_type: NodeType = NodeType.CONTEXT,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
    ) -> str:
        """Manually add a memory node"""
        if not self.initialized:
            await self.initialize()
        
        node_id = f"memory_{uuid.uuid4()}"
        node = MemoryNode(
            id=node_id,
            type=node_type,
            content=content,
            metadata=metadata or {},
            importance=importance,
        )
        self.memory.add_node(node)
        
        await self.storage.save_memory_graph(self.memory)
        return node_id
    
    async def search_memory(self, query: str, limit: int = 10) -> List[MemoryNode]:
        """Search memory for relevant nodes"""
        if not self.initialized:
            await self.initialize()
        
        return self.memory.find_nodes(query=query, limit=limit)
    
    async def get_context(self, query: str, max_nodes: int = 20) -> List[MemoryNode]:
        """Get relevant context for a query"""
        if not self.initialized:
            await self.initialize()
        
        return self.memory.get_context(query, max_nodes=max_nodes)
    
    def sync(self):
        """Synchronous wrapper for async operations"""
        return asyncio.run(self.process)


