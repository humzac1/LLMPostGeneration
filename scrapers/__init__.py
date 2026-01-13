"""
Scrapers module for fetching content from social media platforms
"""

from .linkedin_scraper import scrape_linkedin_posts
from .x_scraper import scrape_x_posts

__all__ = ['scrape_linkedin_posts', 'scrape_x_posts']

