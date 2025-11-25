"""
Scrape Agent: Extracts profile data
"""

import asyncio
import logging
import random
from typing import Optional, Dict, List
from scraper.browser_controller import BrowserController
from scraper.data_extractor import DataExtractor
from scraper.human_behavior import HumanBehavior

logger = logging.getLogger(__name__)


class ScrapeAgent:
    """Agent for scraping profile data"""
    
    def __init__(self, browser_controller: BrowserController, data_extractor: DataExtractor):
        self.browser = browser_controller
        self.data_extractor = data_extractor
        self.human_behavior = HumanBehavior()
    
    async def scrape_profile(self, profile_url: str) -> Optional[Dict]:
        """Scrape single profile with comprehensive extraction"""
        try:
            logger.info(f"[SCRAPE] Scraping profile: {profile_url}")
            
            # Navigate to profile with extended timeout and retry
            if not await self.browser.navigate(profile_url, wait_until='domcontentloaded', timeout=60000, max_retries=3):
                logger.warning(f"[WARN] Failed to navigate to {profile_url}")
                return None
            
            # Wait for page to stabilize after navigation
            await self.human_behavior.random_delay(1, 2)
            
            # Close any modal dialogs (e.g., app upsell prompts)
            try:
                # Try multiple selector strategies to close modals
                modal_selectors = [
                    'button[aria-label="Close"]',
                    'button[aria-label="Dismiss"]',
                    '[role="dialog"] button:first-child',
                    '.cta-modal button',
                ]
                for selector in modal_selectors:
                    try:
                        close_btn = await self.browser.page.query_selector(selector)
                        if close_btn:
                            await close_btn.click()
                            await self.human_behavior.random_delay(0.5, 1)
                            break
                    except:
                        pass
            except:
                pass
            
            # Check for access issues
            if await self._check_profile_access_issues():
                logger.warning(f"Profile access restricted: {profile_url}")
                return None
            
            # Human-like behavior
            await self.human_behavior.human_scroll(self.browser.page, scroll_pattern='natural')
            await self.human_behavior.random_mouse_movement(self.browser.page)
            await self.human_behavior.random_delay(2, 4)
            
            # Expand sections
            await self._expand_all_sections()
            
            # Extract data
            profile_data = await self.data_extractor.extract_complete_profile(
                self.browser.page,
                profile_url
            )
            
            if profile_data:
                logger.info(f"Successfully scraped: {profile_data.get('name', 'Unknown')}")
                return profile_data
            else:
                logger.warning(f"No data extracted from: {profile_url}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {profile_url}: {e}")
            return None
    
    async def _check_profile_access_issues(self) -> bool:
        """Check if profile has access restrictions - strict check"""
        try:
            page_content = await self.browser.get_page_content()
            page_text = page_content.lower()
            
            # More specific access issue patterns
            access_issues = [
                "this profile is not available",
                "you cannot view this profile",
                "profile is not public",
                "profile private",
                "404 error",
                "not found",
            ]
            
            return any(issue.lower() in page_text for issue in access_issues)
            
        except Exception as e:
            logger.debug(f"Error checking access: {e}")
            return False
    
    async def _expand_all_sections(self):
        """Expand all collapsible sections on profile - comprehensive approach"""
        try:
            # Close any modal dialogs that might interfere
            try:
                close_buttons = await self.browser.page.query_selector_all(
                    'button[aria-label="Close"], button[aria-label="Dismiss"], [role="dialog"] button:first-child'
                )
                for btn in close_buttons[:3]:  # Close first 3 modals
                    try:
                        await btn.click()
                        await self.human_behavior.random_delay(0.5, 1)
                    except:
                        pass
            except:
                pass
            
            # Multiple passes to catch dynamically generated buttons
            expand_attempts = 0
            max_attempts = 3
            
            while expand_attempts < max_attempts:
                expand_attempts += 1
                
                # Find all expandable elements with multiple selectors
                buttons = await self.browser.page.query_selector_all(
                    'button[aria-expanded="false"], '
                    'button:has-text("Show more"), '
                    'button:has-text("See more"), '
                    'button:has-text("See all"), '
                    '.inline-show-more-text__button, '
                    '[class*="show-more"] button'
                )
                
                logger.debug(f"Expansion attempt {expand_attempts}: Found {len(buttons)} expandable sections")
                
                if len(buttons) == 0:
                    break
                
                for i, button in enumerate(buttons[:20]):  # Increase limit
                    try:
                        await button.scroll_into_view_if_needed()
                        await self.human_behavior.random_delay(0.2, 0.6)
                        await button.click()
                        await self.human_behavior.random_delay(0.4, 1.2)
                        
                        # Occasional longer pause
                        if i % 5 == 0:
                            await self.human_behavior.random_delay(1, 2)
                            
                    except Exception as e:
                        logger.debug(f"Could not expand section {i}: {e}")
                        continue
                
                # Small delay between passes
                await self.human_behavior.random_delay(1, 2)
                    
        except Exception as e:
            logger.debug(f"Error expanding sections: {e}")
    
    async def scrape_multiple_profiles(self, profile_urls: List[str], 
                                     delay_range: tuple = (15, 30)) -> Dict[str, Dict]:
        """Scrape multiple profiles with intelligent delays"""
        results = {
            'total': len(profile_urls),
            'successful': 0,
            'failed': 0,
            'profiles': []
        }
        
        for i, profile_url in enumerate(profile_urls, 1):
            try:
                logger.info(f"Progress: {i}/{len(profile_urls)} ({i/len(profile_urls)*100:.1f}%)")
                
                # Intelligent rate limiting
                if i > 1:
                    await self._adaptive_delay(i, len(profile_urls), delay_range)
                
                # Scrape profile
                profile_data = await self.scrape_profile(profile_url)
                
                if profile_data:
                    results['successful'] += 1
                    results['profiles'].append(profile_data)
                else:
                    results['failed'] += 1
                
            except Exception as e:
                logger.error(f"Error in bulk scrape: {e}")
                results['failed'] += 1
                continue
        
        logger.info(f"Scraping completed: {results['successful']}/{results['total']} successful")
        return results
    
    async def _adaptive_delay(self, current: int, total: int, base_range: tuple):
        """Intelligent delay that adapts based on progress"""
        base_min, base_max = base_range
        
        # Increase delay as progress increases (LinkedIn detects patterns)
        progress_factor = current / total
        
        if progress_factor > 0.7:  # Last 30%
            delay_min = base_min * 1.5
            delay_max = base_max * 1.5
        elif progress_factor > 0.9:  # Last 10%
            delay_min = base_min * 2.0
            delay_max = base_max * 2.0
        else:
            delay_min = base_min
            delay_max = base_max
        
        delay = random.uniform(delay_min, delay_max)
        logger.info(f"⏳ Waiting {delay:.1f} seconds (anti-detection)...")
        await asyncio.sleep(delay)
