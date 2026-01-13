"""
Orchestrator Agent - Master agent that coordinates sub-agents and validates output
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import config
from .linkedin_agent import LinkedInAgent
from .x_agent import XAgent


class OrchestratorAgent(Agent):
    """
    Master Orchestrator Agent that coordinates LinkedIn and X agents,
    ensures parallel execution, and validates final output
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="Master Orchestrator",
            model=OpenAIChat(
                id=config.OPENAI_MODEL,
                api_key=config.OPENAI_API_KEY
            ),
            instructions=config.ORCHESTRATOR_SYSTEM_PROMPT,
            markdown=True,
            **kwargs
        )
        
        # Initialize sub-agents
        self.linkedin_agent = LinkedInAgent()
        self.x_agent = XAgent()
    
    def execute_workflow(
        self, 
        context: str, 
        examples: str, 
        num_posts: int
    ) -> Dict[str, Any]:
        """
        Execute the complete workflow with parallel agent execution
        
        Args:
            context: Context/topic for the posts
            examples: Example posts for style reference
            num_posts: Number of posts to generate per platform
            
        Returns:
            Dictionary containing validated and organized final output
        """
        print("🚀 Starting Thought Leadership Workflow...")
        print(f"📝 Context length: {len(context)} characters")
        print(f"📋 Examples length: {len(examples)} characters")
        print(f"🔢 Posts requested per platform: {num_posts}")
        print("\n" + "="*70)
        
        # Execute sub-agents in parallel
        print("\n⚡ Executing LinkedIn and X agents in parallel...")
        linkedin_output, x_output = self._execute_agents_parallel(
            context, examples, num_posts
        )
        
        print("✅ Both agents completed successfully!")
        print("\n" + "="*70)
        
        # Validate and compile final output
        print("\n🔍 Validating generated content...")
        final_output = self._validate_and_compile(
            context, examples, linkedin_output, x_output
        )
        
        print("✅ Validation complete!")
        print("\n" + "="*70)
        
        return final_output
    
    def _execute_agents_parallel(
        self, 
        context: str, 
        examples: str, 
        num_posts: int
    ) -> tuple:
        """
        Execute LinkedIn and X agents in parallel using ThreadPoolExecutor
        
        Returns:
            Tuple of (linkedin_output, x_output)
        """
        linkedin_output = None
        x_output = None
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both agent tasks
            future_to_agent = {
                executor.submit(
                    self.linkedin_agent.generate_posts, 
                    context, 
                    examples, 
                    num_posts
                ): "LinkedIn",
                executor.submit(
                    self.x_agent.generate_posts, 
                    context, 
                    examples, 
                    num_posts
                ): "X"
            }
            
            # Wait for both to complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result()
                    print(f"✓ {agent_name} Agent completed")
                    
                    if agent_name == "LinkedIn":
                        linkedin_output = result
                    else:
                        x_output = result
                        
                except Exception as e:
                    print(f"✗ {agent_name} Agent failed: {str(e)}")
                    raise
        
        return linkedin_output, x_output
    
    def _validate_and_compile(
        self,
        context: str,
        examples: str,
        linkedin_output: Dict[str, Any],
        x_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate generated content and compile into final cohesive output
        
        Returns:
            Dictionary with validated and organized final output
        """
        # Create validation prompt
        validation_prompt = config.VALIDATION_PROMPT_TEMPLATE.format(
            context=context,
            examples=examples,
            linkedin_posts=linkedin_output['posts'],
            x_posts=x_output['posts']
        )
        
        # Run validation through the orchestrator
        validation_response = self.run(validation_prompt)
        validation_summary = (
            validation_response.content 
            if hasattr(validation_response, 'content') 
            else str(validation_response)
        )
        
        # Compile final output
        final_output = {
            "workflow_status": "completed",
            "metadata": {
                "context_provided": context[:100] + "..." if len(context) > 100 else context,
                "total_linkedin_posts": linkedin_output['num_posts'],
                "total_x_posts": x_output['num_posts'],
                "agents_used": [
                    linkedin_output['agent'],
                    x_output['agent'],
                    self.name
                ]
            },
            "validation_summary": validation_summary,
            "linkedin_posts": {
                "platform": linkedin_output['platform'],
                "count": linkedin_output['num_posts'],
                "content": linkedin_output['posts']
            },
            "x_posts": {
                "platform": x_output['platform'],
                "count": x_output['num_posts'],
                "content": x_output['posts']
            }
        }
        
        return final_output
    
    def format_output(self, final_output: Dict[str, Any]) -> str:
        """
        Format the final output for display
        
        Returns:
            Formatted string for console output
        """
        output = []
        output.append("\n" + "="*70)
        output.append("📊 FINAL OUTPUT - THOUGHT LEADERSHIP CONTENT")
        output.append("="*70 + "\n")
        
        # Metadata
        output.append("📋 WORKFLOW METADATA")
        output.append("-" * 70)
        output.append(f"Status: {final_output['workflow_status'].upper()}")
        output.append(f"Context: {final_output['metadata']['context_provided']}")
        output.append(f"Agents Involved: {', '.join(final_output['metadata']['agents_used'])}")
        output.append(f"Total LinkedIn Posts: {final_output['metadata']['total_linkedin_posts']}")
        output.append(f"Total X Posts: {final_output['metadata']['total_x_posts']}")
        output.append("\n")
        
        # Validation Summary
        output.append("🔍 VALIDATION SUMMARY")
        output.append("-" * 70)
        output.append(final_output['validation_summary'])
        output.append("\n")
        
        # LinkedIn Posts
        output.append("💼 LINKEDIN POSTS")
        output.append("-" * 70)
        output.append(f"Platform: {final_output['linkedin_posts']['platform']}")
        output.append(f"Count: {final_output['linkedin_posts']['count']}")
        output.append("\n")
        output.append(final_output['linkedin_posts']['content'])
        output.append("\n")
        
        # X Posts
        output.append("🐦 X (TWITTER) POSTS")
        output.append("-" * 70)
        output.append(f"Platform: {final_output['x_posts']['platform']}")
        output.append(f"Count: {final_output['x_posts']['count']}")
        output.append("\n")
        output.append(final_output['x_posts']['content'])
        output.append("\n")
        
        output.append("="*70)
        output.append("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        output.append("="*70)
        
        return "\n".join(output)

