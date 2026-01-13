#!/usr/bin/env python3
"""
Complete Thought Leadership Workflow
1. Scrapes LinkedIn posts with Apify
2. Scrapes X posts with Apify  
3. Uses scraped posts as examples
4. Runs multi-agent system to generate new posts
"""

import sys
from agents.orchestrator_agent import OrchestratorAgent
from scrapers.linkedin_scraper import scrape_and_format_for_workflow as scrape_linkedin
from scrapers.x_scraper import scrape_and_format_for_workflow as scrape_x
import config


def main():
    """
    Complete workflow: Scrape → Generate
    """
    
    # ========================================================================
    # VALIDATION: Check API Keys
    # ========================================================================
    
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "your_openai_api_key_here":
        print("❌ Error: OPENAI_API_KEY not configured!")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    if not config.APIFY_API_TOKEN or config.APIFY_API_TOKEN == "your_apify_api_token_here":
        print("❌ Error: APIFY_API_TOKEN not configured!")
        print("This workflow requires Apify for scraping social media posts")
        print("Please set your Apify API token in the .env file")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🚀 THOUGHT LEADERSHIP WORKFLOW - COMPLETE PIPELINE")
    print("="*70)
    print(f"OpenAI Model: {config.OPENAI_MODEL}")
    print("="*70 + "\n")
    
    # ========================================================================
    # STEP 1: SCRAPE LINKEDIN POSTS
    # ========================================================================
    
    print("📋 STEP 1/4: Scraping LinkedIn posts for style examples...")
    print("-" * 70 + "\n")
    
    # Configure which LinkedIn content to scrape
    linkedin_urls = [
        "https://www.linkedin.com/company/openai",
        "https://www.linkedin.com/search/results/content/?keywords=ai%20automation&origin=FACETED_SEARCH",
    ]
    
    try:
        linkedin_examples = scrape_linkedin(
            urls=linkedin_urls,
            limit_per_source=5
        )
        print("✅ LinkedIn examples scraped\n")
    except Exception as e:
        print(f"❌ LinkedIn scraping failed: {str(e)}")
        print("Using fallback examples...\n")
        linkedin_examples = """
        LinkedIn Example:
        "Customer expectations have never been higher. 
        In 2024, 73% of customers expect immediate responses.
        This is where AI-powered automation becomes essential.
        #CustomerService #AI"
        """
    
    # ========================================================================
    # STEP 2: SCRAPE X (TWITTER) POSTS
    # ========================================================================
    
    print("📋 STEP 2/4: Scraping X posts for style examples...")
    print("-" * 70 + "\n")
    
    # Configure X scraping - can use URLs, search terms, or handles
    x_start_urls = ["https://twitter.com/OpenAI"]
    x_search_terms = ["AI automation"]
    x_handles = []  # Add handles without @ if desired
    
    try:
        x_examples = scrape_x(
            start_urls=x_start_urls if x_start_urls else None,
            search_terms=x_search_terms if x_search_terms else None,
            twitter_handles=x_handles if x_handles else None,
            max_items=20
        )
        print("✅ X examples scraped\n")
    except Exception as e:
        print(f"❌ X scraping failed: {str(e)}")
        print("Using fallback examples...\n")
        x_examples = """
        X Example:
        "AI won't replace customer service agents.
        But agents using AI will replace those who don't.
        #CX #AI"
        """
    
    # ========================================================================
    # STEP 3: DEFINE YOUR CONTEXT
    # ========================================================================
    
    print("📝 STEP 3/4: Preparing context...")
    print("-" * 70 + "\n")
    
    # CUSTOMIZE THIS: Your business/expertise context
    context = """
    We are a B2B SaaS company specializing in AI-powered customer service automation. 
    Our platform helps enterprises reduce support costs by 40% while improving customer 
    satisfaction scores. We focus on enterprise clients in finance, healthcare, and e-commerce 
    sectors. Key differentiators include our proprietary NLP models, seamless CRM integrations, 
    and compliance-first approach.
    """
    
    # Combine scraped examples
    examples = linkedin_examples + "\n\n---\n\n" + x_examples
    
    # Number of posts to generate per platform
    num_posts = 3
    
    # ========================================================================
    # STEP 4: RUN MULTI-AGENT WORKFLOW
    # ========================================================================
    
    print("🤖 STEP 4/4: Running multi-agent content generation...")
    print("-" * 70 + "\n")
    
    try:
        # Initialize the Orchestrator Agent
        orchestrator = OrchestratorAgent()
        
        # Execute the workflow (agents run in parallel)
        final_output = orchestrator.execute_workflow(
            context=context.strip(),
            examples=examples.strip(),
            num_posts=num_posts
        )
        
        # Format and display the output
        formatted_output = orchestrator.format_output(final_output)
        print(formatted_output)
        
        # Save output to file
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(formatted_output)
        print("\n💾 Output saved to output.txt")
        
    except Exception as e:
        print(f"\n❌ Error during workflow execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

