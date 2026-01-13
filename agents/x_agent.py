"""
X Agent - Specialized agent for creating X (Twitter) posts
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from typing import Dict, Any
import config


class XAgent(Agent):
    """Agent specialized in creating concise, impactful X posts"""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="X Content Creator",
            model=OpenAIChat(
                id=config.OPENAI_MODEL,
                api_key=config.OPENAI_API_KEY
            ),
            instructions=config.X_SYSTEM_PROMPT,
            markdown=True,
            **kwargs
        )
    
    def generate_posts(self, context: str, examples: str, num_posts: int) -> Dict[str, Any]:
        """
        Generate X posts based on context and examples
        
        Args:
            context: The context/topic for the posts
            examples: Example posts to match style and tone
            num_posts: Number of posts to generate
            
        Returns:
            Dictionary containing generated posts and metadata
        """
        prompt = f"""Generate {num_posts} unique X (Twitter) posts based on the following:

CONTEXT:
{context}

EXAMPLE POSTS (for style reference):
{examples}

REQUIREMENTS:
- Create {num_posts} distinct, unique X posts
- Each post MUST be under 280 characters (including hashtags)
- Follow the style and tone of the example posts
- Incorporate insights from the context
- Each post should be impactful and shareable
- Number each post clearly (Post 1, Post 2, etc.)
- Include 1-3 relevant hashtags for each post

Format each post clearly with:
---
Post [Number]
[Post content here - UNDER 280 characters]
---
"""
        
        response = self.run(prompt)
        
        return {
            "platform": "X (Twitter)",
            "num_posts": num_posts,
            "posts": response.content if hasattr(response, 'content') else str(response),
            "agent": self.name
        }

