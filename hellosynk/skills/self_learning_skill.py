"""
Self-Learning Skill - Implements MIT SEAL framework for autonomous learning

This skill learns from interactions, stores patterns, generates self-edits,
and improves its performance over time using reinforcement learning principles.
"""

import uuid
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

from hellosynk.skills.base import BaseSkill, SkillParameter
from hellosynk.core.memory import MemoryNode, NodeType, RelationshipType


class SelfLearningSkill(BaseSkill):
    """
    Self-Learning Skill implementing MIT SEAL framework
    
    Key features:
    - Learns from successful interactions
    - Generates self-edits (training data) from patterns
    - Stores learned patterns in memory graph
    - Improves over time using reinforcement learning
    - Adapts behavior based on feedback
    """
    
    name = "self_learning"
    description = "Self-learning skill that improves from interactions using MIT SEAL framework"
    version = "1.0.0"
    author = "HelloSynk Team"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Learning state
        self.learned_patterns: Dict[str, Dict[str, Any]] = {}
        self.success_count: Dict[str, int] = defaultdict(int)
        self.failure_count: Dict[str, int] = defaultdict(int)
        self.self_edits: List[Dict[str, Any]] = []
        
        # SEAL-specific configuration
        self.min_success_threshold = self.get_config("min_success_threshold", 3)
        self.learning_rate = self.get_config("learning_rate", 0.1)
        self.pattern_decay = self.get_config("pattern_decay", 0.95)
        self.max_self_edits = self.get_config("max_self_edits", 100)
    
    def get_parameters(self) -> List[SkillParameter]:
        return [
            SkillParameter(
                name="action",
                type="string",
                description="Action to perform: 'learn', 'recall', 'generate_edits', 'evaluate', or 'adapt'",
                required=True,
            ),
            SkillParameter(
                name="pattern",
                type="string",
                description="Pattern or query to learn/recall (required for learn/recall)",
                required=False,
            ),
            SkillParameter(
                name="context",
                type="object",
                description="Context information for learning (required for learn)",
                required=False,
            ),
            SkillParameter(
                name="outcome",
                type="string",
                description="Outcome of the interaction: 'success' or 'failure' (required for learn)",
                required=False,
            ),
            SkillParameter(
                name="feedback",
                type="string",
                description="User feedback or evaluation (optional)",
                required=False,
            ),
            SkillParameter(
                name="query",
                type="string",
                description="Query for pattern matching (required for recall/adapt)",
                required=False,
            ),
        ]
    
    async def execute(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute self-learning action"""
        validated_params = self.validate_params(params)
        action = validated_params.get("action")
        memory = context.get("memory")
        
        if not memory:
            raise ValueError("Memory graph is required for self-learning skill")
        
        if action == "learn":
            return await self._learn_pattern(validated_params, memory, context)
        elif action == "recall":
            return await self._recall_pattern(validated_params, memory)
        elif action == "generate_edits":
            return await self._generate_self_edits(memory)
        elif action == "evaluate":
            return await self._evaluate_patterns(validated_params, memory)
        elif action == "adapt":
            return await self._adapt_behavior(validated_params, memory, context)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _learn_pattern(
        self,
        params: Dict[str, Any],
        memory: Any,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Learn a pattern from an interaction (SEAL self-edit generation)
        
        This implements the core SEAL principle: learning from interactions
        and generating structured knowledge for future use.
        """
        pattern = params.get("pattern")
        outcome = params.get("outcome", "success")
        feedback = params.get("feedback")
        context_data = params.get("context", {})
        query = context.get("query", "")
        
        if not pattern:
            raise ValueError("Pattern is required for learning")
        
        # Create pattern ID
        pattern_id = f"pattern_{hash(pattern)}_{uuid.uuid4().hex[:8]}"
        
        # Update success/failure counts
        if outcome == "success":
            self.success_count[pattern_id] += 1
        else:
            self.failure_count[pattern_id] += 1
        
        # Calculate pattern strength (reinforcement learning)
        total_attempts = self.success_count[pattern_id] + self.failure_count[pattern_id]
        success_rate = (
            self.success_count[pattern_id] / total_attempts
            if total_attempts > 0
            else 0.5
        )
        
        # Store learned pattern
        learned_pattern = {
            "id": pattern_id,
            "pattern": pattern,
            "context": context_data,
            "query": query,
            "outcome": outcome,
            "feedback": feedback,
            "success_rate": success_rate,
            "success_count": self.success_count[pattern_id],
            "failure_count": self.failure_count[pattern_id],
            "total_attempts": total_attempts,
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "importance": success_rate,  # Higher success rate = higher importance
        }
        
        # Update or create pattern
        if pattern_id in self.learned_patterns:
            # Update existing pattern (weighted average)
            existing = self.learned_patterns[pattern_id]
            existing["success_rate"] = (
                existing["success_rate"] * self.pattern_decay +
                success_rate * (1 - self.pattern_decay)
            )
            existing["last_used"] = datetime.now().isoformat()
            existing["success_count"] = self.success_count[pattern_id]
            existing["failure_count"] = self.failure_count[pattern_id]
            existing["total_attempts"] = total_attempts
            if feedback:
                existing["feedback"] = feedback
        else:
            self.learned_patterns[pattern_id] = learned_pattern
        
        # Store in memory graph (SEAL: persistent knowledge storage)
        pattern_node = MemoryNode(
            id=pattern_id,
            type=NodeType.CONCEPT,
            content=f"Learned pattern: {pattern}\nContext: {json.dumps(context_data)}\nSuccess rate: {success_rate:.2f}",
            metadata={
                "pattern": pattern,
                "context": context_data,
                "query": query,
                "outcome": outcome,
                "feedback": feedback,
                "success_rate": success_rate,
                "success_count": self.success_count[pattern_id],
                "failure_count": self.failure_count[pattern_id],
                "skill": "self_learning",
            },
            importance=success_rate,
        )
        memory.add_node(pattern_node)
        
        # Link to related patterns if query exists
        if query:
            related_nodes = memory.find_nodes(query=query, limit=5)
            for node in related_nodes:
                if node.id != pattern_id:
                    memory.add_edge(
                        node.id,
                        pattern_id,
                        RelationshipType.SIMILAR_TO,
                        metadata={"similarity_score": 0.7},
                    )
        
        # Generate self-edit if pattern is successful (SEAL: self-edit generation)
        if outcome == "success" and success_rate >= 0.7:
            self_edit = self._create_self_edit(learned_pattern, context)
            if self_edit:
                self.self_edits.append(self_edit)
                # Keep only recent self-edits
                if len(self.self_edits) > self.max_self_edits:
                    self.self_edits = self.self_edits[-self.max_self_edits:]
        
        return {
            "success": True,
            "pattern_id": pattern_id,
            "pattern": learned_pattern,
            "message": f"Learned pattern with success rate: {success_rate:.2f}",
            "self_edit_generated": outcome == "success" and success_rate >= 0.7,
        }
    
    async def _recall_pattern(
        self,
        params: Dict[str, Any],
        memory: Any,
    ) -> Dict[str, Any]:
        """Recall learned patterns matching a query"""
        query = params.get("query") or params.get("pattern")
        
        if not query:
            raise ValueError("Query or pattern is required for recall")
        
        # Search memory for relevant patterns
        relevant_nodes = memory.find_nodes(query=query, node_type=NodeType.CONCEPT, limit=10)
        
        # Filter to self-learning patterns
        patterns = []
        for node in relevant_nodes:
            if node.metadata.get("skill") == "self_learning":
                pattern_data = {
                    "id": node.id,
                    "pattern": node.metadata.get("pattern", ""),
                    "context": node.metadata.get("context", {}),
                    "success_rate": node.metadata.get("success_rate", 0.5),
                    "success_count": node.metadata.get("success_count", 0),
                    "failure_count": node.metadata.get("failure_count", 0),
                    "importance": node.importance,
                }
                patterns.append(pattern_data)
        
        # Sort by success rate and importance
        patterns.sort(key=lambda p: (p["success_rate"], p["importance"]), reverse=True)
        
        return {
            "success": True,
            "query": query,
            "patterns": patterns,
            "count": len(patterns),
        }
    
    async def _generate_self_edits(self, memory: Any) -> Dict[str, Any]:
        """
        Generate self-edits from learned patterns (SEAL: self-edit generation)
        
        Self-edits are structured training examples that can be used to
        improve the model's performance.
        """
        # Get high-quality patterns from memory
        all_patterns = memory.find_nodes(node_type=NodeType.CONCEPT, limit=50)
        high_quality_patterns = [
            node for node in all_patterns
            if node.metadata.get("skill") == "self_learning"
            and node.metadata.get("success_rate", 0) >= 0.7
        ]
        
        # Generate self-edits
        generated_edits = []
        for pattern_node in high_quality_patterns[:20]:  # Limit to top 20
            pattern_data = pattern_node.metadata
            self_edit = {
                "instruction": f"Apply pattern: {pattern_data.get('pattern', '')}",
                "input": pattern_data.get("query", ""),
                "context": pattern_data.get("context", {}),
                "expected_output": "success",
                "success_rate": pattern_data.get("success_rate", 0.7),
                "metadata": {
                    "pattern_id": pattern_node.id,
                    "success_count": pattern_data.get("success_count", 0),
                    "created_at": pattern_node.created_at.isoformat(),
                },
            }
            generated_edits.append(self_edit)
        
        return {
            "success": True,
            "self_edits": generated_edits,
            "count": len(generated_edits),
            "total_stored": len(self.self_edits),
        }
    
    async def _evaluate_patterns(
        self,
        params: Dict[str, Any],
        memory: Any,
    ) -> Dict[str, Any]:
        """Evaluate and rank learned patterns"""
        # Get all self-learning patterns
        all_patterns = memory.find_nodes(node_type=NodeType.CONCEPT, limit=100)
        patterns = [
            node for node in all_patterns
            if node.metadata.get("skill") == "self_learning"
        ]
        
        # Calculate evaluation metrics
        evaluations = []
        for pattern_node in patterns:
            pattern_data = pattern_node.metadata
            success_rate = pattern_data.get("success_rate", 0.5)
            total_attempts = (
                pattern_data.get("success_count", 0) +
                pattern_data.get("failure_count", 0)
            )
            
            # Calculate quality score
            quality_score = success_rate * min(total_attempts / 10, 1.0) * pattern_node.importance
            
            evaluations.append({
                "pattern_id": pattern_node.id,
                "pattern": pattern_data.get("pattern", ""),
                "success_rate": success_rate,
                "total_attempts": total_attempts,
                "importance": pattern_node.importance,
                "quality_score": quality_score,
                "last_used": pattern_node.last_accessed.isoformat() if pattern_node.last_accessed else None,
            })
        
        # Sort by quality score
        evaluations.sort(key=lambda e: e["quality_score"], reverse=True)
        
        return {
            "success": True,
            "evaluations": evaluations,
            "total_patterns": len(evaluations),
            "top_patterns": evaluations[:10],
        }
    
    async def _adapt_behavior(
        self,
        params: Dict[str, Any],
        memory: Any,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Adapt behavior based on learned patterns (SEAL: adaptive behavior)
        
        This uses learned patterns to suggest optimal actions for a given query.
        """
        query = params.get("query") or context.get("query", "")
        
        if not query:
            raise ValueError("Query is required for adaptation")
        
        # Find relevant patterns
        relevant_nodes = memory.find_nodes(query=query, node_type=NodeType.CONCEPT, limit=10)
        patterns = [
            node for node in relevant_nodes
            if node.metadata.get("skill") == "self_learning"
            and node.metadata.get("success_rate", 0) >= 0.6
        ]
        
        if not patterns:
            return {
                "success": False,
                "message": "No relevant learned patterns found",
                "suggestion": "Try learning from a successful interaction first",
            }
        
        # Select best pattern (highest success rate and importance)
        best_pattern = max(
            patterns,
            key=lambda p: (
                p.metadata.get("success_rate", 0) * p.importance
            )
        )
        
        pattern_data = best_pattern.metadata
        
        # Generate adaptation suggestion
        adaptation = {
            "pattern_id": best_pattern.id,
            "pattern": pattern_data.get("pattern", ""),
            "context": pattern_data.get("context", {}),
            "success_rate": pattern_data.get("success_rate", 0),
            "confidence": best_pattern.importance * pattern_data.get("success_rate", 0),
            "recommended_action": pattern_data.get("pattern", ""),
            "reasoning": f"Pattern has {pattern_data.get('success_rate', 0):.1%} success rate with {pattern_data.get('success_count', 0)} successes",
        }
        
        return {
            "success": True,
            "query": query,
            "adaptation": adaptation,
            "alternative_patterns": len(patterns) - 1,
        }
    
    def _create_self_edit(
        self,
        pattern: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Create a self-edit from a successful pattern (SEAL: self-edit generation)
        
        Self-edits are structured examples that guide future behavior.
        """
        if pattern.get("success_rate", 0) < 0.7:
            return None
        
        self_edit = {
            "type": "pattern_application",
            "instruction": f"When encountering similar context, apply pattern: {pattern.get('pattern', '')}",
            "input_context": pattern.get("context", {}),
            "input_query": pattern.get("query", ""),
            "expected_behavior": pattern.get("pattern", ""),
            "success_indicators": {
                "success_rate": pattern.get("success_rate", 0),
                "success_count": pattern.get("success_count", 0),
            },
            "metadata": {
                "pattern_id": pattern.get("id"),
                "created_at": datetime.now().isoformat(),
                "source": "self_learning_skill",
            },
        }
        
        return self_edit
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the learning process"""
        total_patterns = len(self.learned_patterns)
        total_successes = sum(self.success_count.values())
        total_failures = sum(self.failure_count.values())
        total_self_edits = len(self.self_edits)
        
        avg_success_rate = (
            sum(p.get("success_rate", 0) for p in self.learned_patterns.values()) / total_patterns
            if total_patterns > 0
            else 0
        )
        
        return {
            "total_patterns": total_patterns,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "total_attempts": total_successes + total_failures,
            "overall_success_rate": (
                total_successes / (total_successes + total_failures)
                if (total_successes + total_failures) > 0
                else 0
            ),
            "average_pattern_success_rate": avg_success_rate,
            "total_self_edits": total_self_edits,
            "learning_rate": self.learning_rate,
        }

