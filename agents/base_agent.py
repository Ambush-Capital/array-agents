#Base agent class with common functionality

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
from openai import OpenAI


class BaseAgent(ABC):
    """
    Abstract base class for all DeFi portfolio optimization agents.
    
    This class defines the common interface and functionality that all agents must implement,
    ensuring consistency across the agent ecosystem while allowing for specialized behavior.
    """

    def __init__(
        self, 
        agent_id: str,
        role: str,
        goal: str,
        backstory: str,
        knowledge_sources: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a base agent with its core properties.
        
        Args:
            agent_id: Unique identifier for the agent
            role: The specific role of this agent in the system
            goal: The primary objective this agent is trying to achieve
            backstory: Background narrative for the agent's persona
            knowledge_sources: List of knowledge sources this agent has access to
            tools: List of tools this agent can use
            config: Additional configuration parameters for the agent
        """
        self.agent_id = agent_id
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.knowledge_sources = knowledge_sources or []
        self.tools = tools or []

        # Store configuration
        self.config = config or {}

        # Set up logger first so we can use it for logging
        self.logger = self._setup_logger()

        # Set up OpenAI client with API key from config if available
        api_key = self.config.get('OPENAI_API_KEY')
        
        # Initialize the OpenAI client
        # If api_key is None, the client will try to use the OPENAI_API_KEY environment variable
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = OpenAI()  # Will automatically look for OPENAI_API_KEY env var
            self.logger.info("No API key provided in config, using environment variables if available.")

    def _setup_logger(self) -> logging.Logger:
        """Set up a logger for the agent."""
        logger = logging.getLogger(f"agent.{self.agent_id}")
        return logger

    @abstractmethod
    def execute_task(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task appropriate for this agent.
        
        Args:
            task_input: The input data and parameters for the task
            
        Returns:
            Dictionary containing the results of the task execution
        """
        pass

    def use_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use a specific tool available to this agent.
        
        Args:
            tool_name: The name of the tool to use
            tool_input: The input data for the tool
            
        Returns:
            Result of the tool execution
        """
        if tool_name not in self.tools:
            self.logger.error(f"Tool '{tool_name}' not available to agent '{self.agent_id}'")
            return {"error": f"Tool '{tool_name}' not available to this agent"}

        # Import the tool dynamically
        try:
            module_path = f"tools.{tool_name}"
            tool_module = __import__(module_path, fromlist=["execute"])
            result = tool_module.execute(tool_input)
            return result
        except Exception as e:
            self.logger.exception(f"Error executing tool '{tool_name}': {str(e)}")
            return {"error": f"Error executing tool: {str(e)}"}

    def access_knowledge(self, source_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Access a specific knowledge source available to this agent.
        
        Args:
            source_name: The name of the knowledge source to access
            query: The query parameters to retrieve specific information
            
        Returns:
            The requested knowledge
        """
        if source_name not in self.knowledge_sources:
            self.logger.error(f"Knowledge source '{source_name}' not available to agent '{self.agent_id}'")
            return {"error": f"Knowledge source '{source_name}' not available to this agent"}

        # Import the knowledge source dynamically
        try:
            module_path = f"knowledge.{source_name}"
            knowledge_module = __import__(module_path, fromlist=["query"])
            result = knowledge_module.query(query)
            return result
        except Exception as e:
            self.logger.exception(f"Error accessing knowledge source '{source_name}': {str(e)}")
            return {"error": f"Error accessing knowledge source: {str(e)}"}

    def save_output(self, output: Any, file_path: str) -> bool:
        """
        Save the agent's output to a file.
        
        Args:
            output: The data to save
            file_path: The path where the output should be saved
            
        Returns:
            True if the save was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            output_dir = Path(file_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Determine the file type and save accordingly
            if file_path.endswith('.json'):
                import json
                with open(file_path, 'w') as f:
                    json.dump(output, f, indent=2)
            elif file_path.endswith('.md'):
                with open(file_path, 'w') as f:
                    f.write(output)
            else:
                # Default to string representation
                with open(file_path, 'w') as f:
                    f.write(str(output))

            self.logger.info(f"Output saved to {file_path}")
            return True
        except Exception as e:
            self.logger.exception(f"Error saving output to {file_path}: {str(e)}")
            return False

    def _build_persona_prompt(self, task_prompt: str) -> str:
        """
        Build a prompt that includes the agent's persona information.
        
        Args:
            task_prompt: The task-specific prompt
            
        Returns:
            A complete prompt with persona context
        """
        persona_prompt = f"""You are acting as a {self.role}.

Your goal: {self.goal}

Your backstory: {self.backstory}

Task: {task_prompt}

Respond in a way that is consistent with your role, goal, and backstory. Focus on providing high-quality, actionable insights.
"""
        return persona_prompt
    
    def call_llm(self, prompt: str, include_persona: bool = True, **kwargs) -> str:
        """Calls the OpenAI LLM with the provided prompt and returns the response text."""
        default_params = {
            "model": "gpt-4o",
            "max_tokens": 3000,
            "temperature": 0.7,
        }
        # Include the agent's persona if requested
        if include_persona:
            final_prompt = self._build_persona_prompt(prompt)
        else:
            final_prompt = prompt
        
        # GPT-4 and newer models require the chat completions API
        if default_params.get("model", kwargs.get("model", "")).startswith(("gpt-4", "gpt-3.5")):
            # Format for chat completions API
            messages = kwargs.pop("messages", [{"role": "user", "content": prompt}])
            params = {**default_params, **kwargs, "messages": messages}
            try:
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content.strip()
            except Exception as e:
                error_msg = str(e)
                if "api_key" in error_msg.lower() or "apikey" in error_msg.lower():
                    self.logger.error("OpenAI API key error: Please set a valid API key in the config or as the OPENAI_API_KEY environment variable")
                else:
                    self.logger.error(f"LLM call failed: {e}")
                raise
        else:
            # Legacy completions API format
            params = {**default_params, **kwargs, "prompt": prompt}
            try:
                response = self.client.completions.create(**params)
                return response.choices[0].text.strip()
            except Exception as e:
                error_msg = str(e)
                if "api_key" in error_msg.lower() or "apikey" in error_msg.lower():
                    self.logger.error("OpenAI API key error: Please set a valid API key in the config or as the OPENAI_API_KEY environment variable")
                else:
                    self.logger.error(f"LLM call failed: {e}")
                raise

    def get_persona(self) -> Dict[str, str]:
        """
        Get the persona information for this agent.
        
        Returns:
            Dictionary containing the agent's persona information
        """
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory
        }

    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.agent_id} ({self.role})"