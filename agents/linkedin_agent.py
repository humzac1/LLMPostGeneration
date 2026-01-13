"""
LinkedIn Agent - Specialized agent for creating LinkedIn posts
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from typing import Dict, Any
import config


class LinkedInAgent(Agent):
    """Agent specialized in creating professional LinkedIn posts"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="LinkedIn Content Creator",
            model=OpenAIChat(
                id=config.OPENAI_MODEL,
                api_key=config.OPENAI_API_KEY
            ),
            instructions=config.LINKEDIN_SYSTEM_PROMPT,
            markdown=True,
            **kwargs
        )
    
    def generate_posts(self, context: str, examples: str, num_posts: int) -> Dict[str, Any]:
        """
        Generate LinkedIn posts based on context and examples
        
        Args:
            context: The context/topic for the posts
            examples: Example posts to match style and tone
            num_posts: Number of posts to generate
            
        Returns:
            Dictionary containing generated posts and metadata
        """
        prompt = f"""Generate {num_posts} unique LinkedIn posts based on the following:

CONTEXT:
{context}

EXAMPLE POSTS (for style reference):
{examples}

REQUIREMENTS:
- Create {num_posts} distinct, unique LinkedIn posts
- Each post should be between 150-300 words
- Follow the style and tone of the example posts
- Incorporate insights from the context
- Each post should be self-contained and valuable
- Number each post clearly (Post 1, Post 2, etc.)
- Include 3-5 relevant hashtags for each post

Format each post clearly with:
---
Post [Number]
[Post content here]
---
"""
        
        response = self.run(prompt)
        
        return {
            "platform": "LinkedIn",
            "num_posts": num_posts,
            "posts": response.content if hasattr(response, 'content') else str(response),
            "agent": self.name
        }

