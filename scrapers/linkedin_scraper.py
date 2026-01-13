"""
LinkedIn Post Scraper using Apify
Scrapes LinkedIn posts from URLs, profiles, or search results
"""

from apify_client import ApifyClient
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import config


def scrape_linkedin_posts(
    urls: List[str],
    limit_per_source: int = 10,
    output_file: str = "linkedin_scraped.txt",
    format_as_examples: bool = True
) -> str:
    """
    Scrape LinkedIn posts using Apify actor
    
    Args:
        urls: List of LinkedIn URLs to scrape (posts, profiles, search results)
        limit_per_source: Maximum number of posts per URL
        output_file: Path to save the raw output
        format_as_examples: If True, format output for use as agent examples
        
    Returns:
        String containing scraped content (formatted if format_as_examples=True)
        
    Raises:
        ValueError: If APIFY_API_TOKEN is not configured
        Exception: If scraping fails
    """
    
    # Check if API token is configured
    if not config.APIFY_API_TOKEN or config.APIFY_API_TOKEN == "your_apify_api_token_here":
        raise ValueError(
            "APIFY_API_TOKEN not configured. "
            "Please set your Apify API token in the .env file"
        )
    
    print(f"🔄 Starting LinkedIn scraping for {len(urls)} URL(s)...")
    
    # Initialize Apify client
    client = ApifyClient(config.APIFY_API_TOKEN)
    
    # Prepare actor input
    run_input = {
        "urls": urls,
        "limitPerSource": limit_per_source,
    }
    
    try:
        # Run the actor
        print("⚙️  Running Apify actor (supreme_coder/linkedin-post)...")
        run = client.actor("supreme_coder/linkedin-post").call(run_input=run_input)
        
        # Collect all items
        items = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)
        
        print(f"✅ Scraped {len(items)} LinkedIn posts")
        
        # Save raw output
        output_path = Path(output_file)
        with output_path.open("w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, indent=2))
                f.write("\n\n---\n\n")
        
        print(f"💾 Raw output saved to: {output_path.resolve()}")
        
        # Format for use as examples if requested
        if format_as_examples:
            formatted_examples = _format_as_examples(items)
            
            # Save formatted examples
            examples_path = Path(output_file.replace('.txt', '_examples.txt'))
            with examples_path.open("w", encoding="utf-8") as f:
                f.write(formatted_examples)
            
            print(f"📝 Formatted examples saved to: {examples_path.resolve()}")
            return formatted_examples
        
        return json.dumps(items, indent=2)
        
    except Exception as e:
        print(f"❌ Error during LinkedIn scraping: {str(e)}")
        raise


def _format_as_examples(items: List[Dict[str, Any]]) -> str:
    """
    Format scraped LinkedIn posts as examples for agent use
    
    Args:
        items: List of scraped post data
        
    Returns:
        Formatted string suitable for agent examples
    """
    examples = []
    
    for idx, item in enumerate(items, 1):
        # Extract relevant fields
        text = item.get('text', '')
        author = item.get('author', {}).get('name', 'Unknown Author')
        url = item.get('url', '')
        
        # Skip if no text content
        if not text or len(text.strip()) < 20:
            continue
        
        # Format as example
        example = f"""LinkedIn Example {idx}:
"{text}"
(Author: {author})
"""
        examples.append(example)
    
    if not examples:
        return "No valid examples found from scraped content."
    
    return "\n---\n\n".join(examples)


def extract_post_text_only(items: List[Dict[str, Any]]) -> List[str]:
    """
    Extract only the text content from scraped posts
    
    Args:
        items: List of scraped post data
        
    Returns:
        List of post text strings
    """
    posts = []
    for item in items:
        text = item.get('text', '').strip()
        if text and len(text) >= 20:
            posts.append(text)
    return posts


def scrape_and_format_for_workflow(
    urls: List[str],
    limit_per_source: int = 10
) -> str:
    """
    Convenience function to scrape LinkedIn posts and format for workflow
    
    Args:
        urls: List of LinkedIn URLs to scrape
        limit_per_source: Maximum posts per URL
        
    Returns:
        Formatted string ready to use as 'examples' in main.py
    """
    return scrape_linkedin_posts(
        urls=urls,
        limit_per_source=limit_per_source,
        format_as_examples=True
    )


if __name__ == "__main__":
    """
    Example usage when run directly
    """
    # Example URLs - modify these for your use case
    example_urls = [
        "https://www.linkedin.com/posts/linkedin_no-is-a-complete-sentence-activity-7247998907798978560-J_hB?utm_source=share&utm_medium=member_desktop",
        "https://www.linkedin.com/company/amazon",
        "https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords=ai&origin=FACETED_SEARCH",
    ]
    
    try:
        formatted_examples = scrape_linkedin_posts(
            urls=example_urls,
            limit_per_source=10,
            output_file="linkedin_scraped.txt",
            format_as_examples=True
        )
        
        print("\n" + "="*70)
        print("📋 FORMATTED EXAMPLES (ready for workflow)")
        print("="*70)
        print(formatted_examples)
        
    except Exception as e:
        print(f"\n❌ Failed to scrape: {str(e)}")
        print("\nMake sure:")
        print("1. APIFY_API_TOKEN is set in .env")
        print("2. You have internet connection")
        print("3. Your Apify account has sufficient credits")

