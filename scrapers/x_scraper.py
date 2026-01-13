"""
X (Twitter) Post Scraper using Apify
Scrapes X posts from URLs, profiles, search terms, or handles
"""

from apify_client import ApifyClient
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import config


def scrape_x_posts(
    start_urls: Optional[List[str]] = None,
    search_terms: Optional[List[str]] = None,
    twitter_handles: Optional[List[str]] = None,
    max_items: int = 100,
    sort: str = "Latest",
    tweet_language: str = "en",
    output_file: str = "x_scraped.txt",
    format_as_examples: bool = True
) -> str:
    """
    Scrape X (Twitter) posts using Apify actor
    
    Args:
        start_urls: List of Twitter URLs to scrape (profiles, searches, lists)
        search_terms: List of search terms to find tweets
        twitter_handles: List of Twitter handles to scrape
        max_items: Maximum number of tweets to scrape
        sort: Sort order ("Latest", "Top", "Hot")
        tweet_language: Language code (e.g., "en", "es", "fr")
        output_file: Path to save the raw output
        format_as_examples: If True, format output for use as agent examples
        
    Returns:
        String containing scraped content (formatted if format_as_examples=True)
        
    Raises:
        ValueError: If APIFY_API_TOKEN is not configured or no input provided
        Exception: If scraping fails
    """
    
    # Check if API token is configured
    if not config.APIFY_API_TOKEN or config.APIFY_API_TOKEN == "your_apify_api_token_here":
        raise ValueError(
            "APIFY_API_TOKEN not configured. "
            "Please set your Apify API token in the .env file"
        )
    
    # Validate that at least one input method is provided
    if not any([start_urls, search_terms, twitter_handles]):
        raise ValueError(
            "Must provide at least one of: start_urls, search_terms, or twitter_handles"
        )
    
    input_count = sum([
        len(start_urls) if start_urls else 0,
        len(search_terms) if search_terms else 0,
        len(twitter_handles) if twitter_handles else 0
    ])
    
    print(f"🔄 Starting X/Twitter scraping ({input_count} source(s), max {max_items} items)...")
    
    # Initialize Apify client
    client = ApifyClient(config.APIFY_API_TOKEN)
    
    # Prepare actor input
    run_input = {
        "maxItems": max_items,
        "sort": sort,
        "tweetLanguage": tweet_language,
        "customMapFunction": "(object) => { return {...object} }",
    }
    
    # Add optional inputs
    if start_urls:
        run_input["startUrls"] = start_urls
    if search_terms:
        run_input["searchTerms"] = search_terms
    if twitter_handles:
        run_input["twitterHandles"] = twitter_handles
    
    try:
        # Run the actor
        print("⚙️  Running Apify actor (apidojo/tweet-scraper)...")
        run = client.actor("apidojo/tweet-scraper").call(run_input=run_input)
        
        dataset_url = f"https://console.apify.com/storage/datasets/{run['defaultDatasetId']}"
        print(f"💾 Dataset: {dataset_url}")
        
        # Collect all items
        items = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)
        
        print(f"✅ Scraped {len(items)} X posts")
        
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
        print(f"❌ Error during X scraping: {str(e)}")
        raise


def _format_as_examples(items: List[Dict[str, Any]]) -> str:
    """
    Format scraped X posts as examples for agent use
    
    Args:
        items: List of scraped tweet data
        
    Returns:
        Formatted string suitable for agent examples
    """
    examples = []
    
    for idx, item in enumerate(items, 1):
        # Extract relevant fields (handle different response structures)
        text = item.get('text', item.get('full_text', ''))
        author = item.get('author', {})
        
        # Handle author as dict or string
        if isinstance(author, dict):
            author_name = author.get('userName', author.get('name', 'Unknown Author'))
        else:
            author_name = str(author) if author else 'Unknown Author'
        
        url = item.get('url', '')
        
        # Skip if no text content
        if not text or len(text.strip()) < 10:
            continue
        
        # Skip retweets if they're just prefixed text
        if text.startswith('RT @'):
            continue
        
        # Ensure tweet is under 280 characters (or close to it)
        # Some scraped tweets might include quoted text
        if len(text) > 400:  # Skip unusually long entries
            continue
        
        # Format as example
        example = f"""X Example {idx}:
"{text}"
(Author: @{author_name})
"""
        examples.append(example)
    
    if not examples:
        return "No valid examples found from scraped content."
    
    return "\n---\n\n".join(examples)


def extract_post_text_only(items: List[Dict[str, Any]]) -> List[str]:
    """
    Extract only the text content from scraped tweets
    
    Args:
        items: List of scraped tweet data
        
    Returns:
        List of tweet text strings
    """
    posts = []
    for item in items:
        text = item.get('text', item.get('full_text', '')).strip()
        if text and len(text) >= 10 and not text.startswith('RT @'):
            posts.append(text)
    return posts


def scrape_and_format_for_workflow(
    start_urls: Optional[List[str]] = None,
    search_terms: Optional[List[str]] = None,
    twitter_handles: Optional[List[str]] = None,
    max_items: int = 50
) -> str:
    """
    Convenience function to scrape X posts and format for workflow
    
    Args:
        start_urls: List of Twitter URLs to scrape
        search_terms: List of search terms
        twitter_handles: List of Twitter handles (without @)
        max_items: Maximum tweets to scrape
        
    Returns:
        Formatted string ready to use as 'examples' in main.py
    """
    return scrape_x_posts(
        start_urls=start_urls,
        search_terms=search_terms,
        twitter_handles=twitter_handles,
        max_items=max_items,
        format_as_examples=True
    )


if __name__ == "__main__":
    """
    Example usage when run directly
    """
    # Example configuration - modify these for your use case
    example_start_urls = [
        "https://twitter.com/OpenAI",
        "https://twitter.com/search?q=AI%20automation&src=typed_query",
    ]
    
    example_search_terms = [
        "AI automation",
        "thought leadership",
    ]
    
    example_twitter_handles = [
        "OpenAI",
        "sama",
    ]
    
    try:
        # You can use any combination of start_urls, search_terms, or twitter_handles
        formatted_examples = scrape_x_posts(
            start_urls=example_start_urls,
            # search_terms=example_search_terms,  # Uncomment to use
            # twitter_handles=example_twitter_handles,  # Uncomment to use
            max_items=20,
            sort="Latest",
            tweet_language="en",
            output_file="x_scraped.txt",
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

