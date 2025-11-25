"""
Advanced JavaScript-Based Data Extractor
- Extracts data using JavaScript evaluation for reliable parsing
- Text-based extraction resistant to HTML changes
- Dynamic section detection with intelligent fallbacks
- Completeness scoring (0-100%)
"""

import re
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extract LinkedIn profile data using JavaScript evaluation + text parsing"""
    
    def __init__(self):
        self.extracted_data = {}
    
    async def extract_complete_profile(self, page: Page, profile_url: str) -> Optional[Dict]:
        """Extract complete profile using JavaScript evaluation"""
        try:
            logger.info(f"Extracting profile data from {profile_url}")
            
            # Get all page text via JavaScript (most reliable method)
            all_text = await self._extract_all_with_js(page)
            
            if not all_text:
                logger.warning("Could not extract page content")
                return None
            
            profile_data = {
                'profile_url': profile_url,
                'scraped_at': datetime.now().isoformat(),
                'extraction_method': 'javascript-text-based'
            }
            
            # Extract basic info - use JavaScript first, then text fallbacks
            profile_data['name'] = await self._extract_name(page, all_text)
            profile_data['headline'] = await self._extract_headline(page, all_text)
            profile_data['location'] = await self._extract_location(page, all_text)
            profile_data['about'] = await self._extract_about(page, all_text)
            
            # Extract sections using text parsing
            profile_data['experience'] = await self._extract_experience(page, all_text)
            profile_data['education'] = await self._extract_education(page, all_text)
            profile_data['skills'] = await self._extract_skills(page, all_text)
            profile_data['certifications'] = await self._extract_certifications(page, all_text)
            profile_data['projects'] = await self._extract_projects(page, all_text)
            profile_data['languages'] = await self._extract_languages(page, all_text)
            profile_data['recommendations'] = await self._extract_recommendations(page, all_text)
            
            # Calculate completeness score
            profile_data['completeness'] = self._calculate_completeness(profile_data)
            
            logger.info(f"Profile extraction completed: {profile_data.get('name', 'Unknown')} ({profile_data['completeness']}% complete)")
            return profile_data
            
        except Exception as e:
            logger.error(f"Profile extraction failed: {e}")
            return None
    
    async def _extract_all_with_js(self, page: Page) -> Optional[str]:
        """Extract all page text using JavaScript - most reliable method"""
        try:
            all_text = await page.evaluate("""
                () => {
                    // Get all visible text from page
                    const allText = document.body.innerText;
                    return allText || null;
                }
            """)
            return all_text
        except Exception as e:
            logger.warning(f"Error extracting with JavaScript: {e}")
            return None
    
    async def _extract_name(self, page: Page, all_text: str) -> Optional[str]:
        """Extract name using JavaScript first, then fallback to text"""
        try:
            # Method 1: JavaScript extraction
            name = await page.evaluate("""
                () => {
                    // Try h1 first (usually has the name)
                    const h1 = document.querySelector('h1');
                    if (h1) return h1.innerText.trim();
                    
                    // Try button with name-like content
                    const buttons = document.querySelectorAll('button');
                    for (let btn of buttons) {
                        const text = btn.innerText;
                        if (text && text.length > 3 && text.length < 100 && !text.includes('http')) {
                            return text.trim();
                        }
                    }
                    return null;
                }
            """)
            
            if name and len(name) < 100:
                return name.strip()
            
            # Method 2: Text fallback
            return await self._extract_name_fallback(all_text)
            
        except Exception as e:
            logger.debug(f"Error extracting name: {e}")
            return await self._extract_name_fallback(all_text)
    
    async def _extract_name_fallback(self, all_text: str) -> Optional[str]:
        """Fallback name extraction from text"""
        try:
            lines = all_text.split('\n')
            # First non-empty line under profile heading is often the name
            for line in lines[:20]:
                line = line.strip()
                if line and len(line) > 3 and len(line) < 100 and not any(c.isdigit() for c in line[:5]):
                    # Avoid keywords
                    if not any(kw in line for kw in ['button', 'http', 'Follow', 'Message', 'More']):
                        return line
            return None
        except:
            return None
    
    async def _extract_headline(self, page: Page, all_text: str) -> Optional[str]:
        """Extract headline using JavaScript + text fallback"""
        try:
            # JavaScript method
            headline = await page.evaluate("""
                () => {
                    // Look for divs with role="main" or class containing headline
                    const divs = document.querySelectorAll('[class*="headline"], [class*="title"]');
                    for (let div of divs) {
                        const text = div.innerText;
                        if (text && text.length > 5 && text.length < 300) {
                            return text.trim();
                        }
                    }
                    return null;
                }
            """)
            
            if headline:
                return headline.strip()
            
            # Text fallback
            return await self._extract_headline_fallback(all_text)
            
        except Exception as e:
            logger.debug(f"Error extracting headline: {e}")
            return await self._extract_headline_fallback(all_text)
    
    async def _extract_headline_fallback(self, all_text: str) -> Optional[str]:
        """Fallback headline extraction"""
        try:
            lines = all_text.split('\n')
            # Headline is usually 2nd-3rd line and contains job titles
            job_keywords = ['Engineer', 'Manager', 'Developer', 'Analyst', 'Consultant', 
                          'Specialist', 'Director', 'Lead', 'Sr.', 'Senior', 'Junior']
            
            for line in lines[1:10]:
                line = line.strip()
                if any(keyword in line for keyword in job_keywords) and len(line) > 5 and len(line) < 300:
                    return line
            return None
        except:
            return None
    
    async def _extract_location(self, page: Page, all_text: str) -> Optional[str]:
        """Extract location"""
        try:
            lines = all_text.split('\n')
            # Location usually has commas and appears early in profile
            for line in lines[:15]:
                line = line.strip()
                # Look for patterns like "City, Country" or location keywords
                if ',' in line and len(line) > 3 and len(line) < 100:
                    if not any(x in line for x in ['http', 'button', 'Follow', 'Message']):
                        return line
                if any(loc_word in line for loc_word in ['Area', 'Remote', 'Based']):
                    return line
            return None
        except:
            return None
    
    async def _extract_about(self, page: Page, all_text: str) -> Optional[str]:
        """Extract About section"""
        try:
            lines = all_text.split('\n')
            about_started = False
            about_text = []
            
            for i, line in enumerate(lines):
                if 'About' in line:
                    about_started = True
                    continue
                
                if about_started:
                    # Stop at next section
                    if any(section in line for section in ['Experience', 'Education', 'Skills', 'Licenses']):
                        break
                    
                    line = line.strip()
                    if line and not any(x in line for x in ['http', 'button', 'Follow']):
                        about_text.append(line)
            
            return ' '.join(about_text).strip() if about_text else None
            
        except Exception as e:
            logger.debug(f"Error extracting about: {e}")
            return None
    
    async def _extract_experience(self, page: Page, all_text: str) -> List[Dict]:
        """Extract experience entries from text (robust section detection)"""
        experiences = []
        try:
            lines = all_text.split('\n')
            exp_started = False
            current_exp = None
            section_headers = ['experience', 'work experience', 'professional experience']
            stop_sections = ['education', 'skills', 'licenses', 'certifications', 'projects', 'languages', 'recommendations']
            for i, line in enumerate(lines):
                line_clean = line.strip().lower()
                # Start of experience section (case-insensitive, alternate names)
                if any(h in line_clean for h in section_headers) and not exp_started:
                    exp_started = True
                    continue
                # Stop at next major section
                if exp_started and any(section in line_clean for section in stop_sections):
                    if current_exp and current_exp.get('title'):
                        experiences.append(current_exp)
                    break
                if exp_started and line:
                    # New job entry - starts with job title (no special characters)
                    if not any(c in line.lower() for c in ['http', 'follow', 'endorse', 'button']) and len(line) > 5:
                        if current_exp and current_exp.get('title'):
                            experiences.append(current_exp)
                        current_exp = {'title': line}
                    elif current_exp:
                        if 'company' not in current_exp and (any(x in line for x in ['Inc', 'Ltd', ',']) or len(line) > 20):
                            current_exp['company'] = line
                        elif 'duration' not in current_exp and any(c.isdigit() for c in line):
                            current_exp['duration'] = line
                        elif 'description' not in current_exp and len(line) > 10:
                            current_exp['description'] = line
            if current_exp and current_exp.get('title'):
                experiences.append(current_exp)
            logger.info(f"Extracted {len(experiences)} experience entries")
            return experiences
        except Exception as e:
            logger.warning(f"Error extracting experience: {e}")
            return experiences
    
    async def _extract_education(self, page: Page, all_text: str) -> List[Dict]:
        """Extract education entries (robust section detection)"""
        education = []
        try:
            lines = all_text.split('\n')
            edu_started = False
            current_edu = None
            section_headers = ['education', 'academic background', 'studies']
            stop_sections = ['skills', 'licenses', 'projects', 'languages', 'recommendations', 'experience']
            for line in lines:
                line_clean = line.strip().lower()
                if any(h in line_clean for h in section_headers) and not edu_started:
                    edu_started = True
                    continue
                if edu_started and any(section in line_clean for section in stop_sections):
                    if current_edu and current_edu.get('school'):
                        education.append(current_edu)
                    break
                if edu_started and line:
                    if not any(c in line.lower() for c in ['http', 'follow', 'button']) and len(line) > 3:
                        if 'school' not in current_edu if current_edu else True:
                            if current_edu and current_edu.get('school'):
                                education.append(current_edu)
                            current_edu = {'school': line}
                        elif current_edu:
                            if 'degree' not in current_edu:
                                current_edu['degree'] = line
                            elif 'duration' not in current_edu and any(c.isdigit() for c in line):
                                current_edu['duration'] = line
            if current_edu and current_edu.get('school'):
                education.append(current_edu)
            logger.info(f"Extracted {len(education)} education entries")
            return education
        except Exception as e:
            logger.warning(f"Error extracting education: {e}")
            return education
    
    async def _extract_skills(self, page: Page, all_text: str) -> List[str]:
        """Extract skills list (robust section detection)"""
        skills = []
        try:
            lines = all_text.split('\n')
            skill_started = False
            section_headers = ['skills', 'core skills', 'competencies']
            stop_sections = ['licenses', 'projects', 'languages', 'certifications', 'recommendations', 'education', 'experience']
            for line in lines:
                line_clean = line.strip().lower()
                if any(h in line_clean for h in section_headers):
                    skill_started = True
                    continue
                if skill_started:
                    if any(section in line_clean for section in stop_sections):
                        break
                    if line and not any(c in line.lower() for c in ['http', 'follow', 'endorse', 'button']):
                        skill_clean = re.sub(r'\d+\s*(endorsements?)?', '', line, flags=re.IGNORECASE).strip()
                        if skill_clean and len(skill_clean) > 1 and len(skill_clean) < 100:
                            skills.append(skill_clean)
            skills = list(dict.fromkeys(skills))
            logger.info(f"Extracted {len(skills)} skills")
        except Exception as e:
            logger.warning(f"Error extracting skills: {e}")
        return skills
    
    async def _extract_certifications(self, page: Page, all_text: str) -> List[Dict]:
        """Extract certifications"""
        certs = []
        try:
            lines = all_text.split('\n')
            cert_started = False
            current_cert = None
            
            for line in lines:
                line = line.strip()
                
                if 'Licenses' in line or 'Certifications' in line:
                    cert_started = True
                    continue
                
                if cert_started and any(section in line for section in ['Projects', 'Languages', 'Skills']):
                    if current_cert and current_cert.get('name'):
                        certs.append(current_cert)
                    break
                
                if cert_started and line:
                    if 'name' not in (current_cert or {}):
                        current_cert = {'name': line}
                    elif current_cert:
                        if 'issuer' not in current_cert:
                            current_cert['issuer'] = line
                        elif 'date' not in current_cert and any(c.isdigit() for c in line):
                            current_cert['date'] = line
            
            if current_cert and current_cert.get('name'):
                certs.append(current_cert)
            
            logger.info(f"Extracted {len(certs)} certifications")
            return certs
            
        except Exception as e:
            logger.warning(f"Error extracting certifications: {e}")
            return certs
    
    async def _extract_projects(self, page: Page, all_text: str) -> List[Dict]:
        """Extract projects"""
        projects = []
        try:
            lines = all_text.split('\n')
            proj_started = False
            current_proj = None
            
            for line in lines:
                line = line.strip()
                
                if 'Projects' in line:
                    proj_started = True
                    continue
                
                if proj_started and any(section in line for section in ['Languages', 'Recommendations', 'Skills']):
                    if current_proj and current_proj.get('name'):
                        projects.append(current_proj)
                    break
                
                if proj_started and line and len(line) > 3:
                    if 'name' not in (current_proj or {}):
                        current_proj = {'name': line}
                    elif current_proj and 'description' not in current_proj:
                        current_proj['description'] = line
            
            if current_proj and current_proj.get('name'):
                projects.append(current_proj)
            
            return projects
            
        except Exception as e:
            logger.warning(f"Error extracting projects: {e}")
            return projects
    
    async def _extract_languages(self, page: Page, all_text: str) -> List[str]:
        """Extract languages"""
        languages = []
        try:
            lines = all_text.split('\n')
            lang_started = False
            
            for line in lines:
                line = line.strip()
                
                if line == 'Languages':
                    lang_started = True
                    continue
                
                if lang_started:
                    if any(section in line for section in ['Recommendations', 'Projects', 'Skills', 'Education']):
                        break
                    
                    if line and not any(c in line for c in ['http', 'Follow', 'button']):
                        if len(line) > 1 and len(line) < 50:
                            languages.append(line)
            
            languages = list(dict.fromkeys(languages))  # Remove duplicates
            
        except Exception as e:
            logger.warning(f"Error extracting languages: {e}")
        
        return languages
    
    async def _extract_recommendations(self, page: Page, all_text: str) -> List[Dict]:
        """Extract recommendations"""
        recommendations = []
        try:
            # Try to extract from page
            rec_data = await page.evaluate("""
                () => {
                    const recs = [];
                    const divs = document.querySelectorAll('[class*="recommendation"]');
                    
                    for (let div of divs) {
                        const text = div.innerText;
                        if (text && text.length > 20) {
                            recs.push({text: text.substring(0, 500)});
                        }
                    }
                    return recs;
                }
            """)
            
            recommendations = rec_data[:5] if rec_data else []
            
        except Exception as e:
            logger.debug(f"Error extracting recommendations: {e}")
        
        return recommendations
    
    def _calculate_completeness(self, profile_data: Dict) -> int:
        """Calculate profile completeness score (0-100%)"""
        try:
            fields = [
                profile_data.get('name'),
                profile_data.get('headline'),
                profile_data.get('location'),
                profile_data.get('about'),
                profile_data.get('experience'),
                profile_data.get('education'),
                profile_data.get('skills'),
            ]
            
            # Count non-empty fields
            filled = sum(1 for field in fields if field)
            completeness = (filled / len(fields)) * 100
            
            return int(completeness)
            
        except Exception as e:
            logger.debug(f"Error calculating completeness: {e}")
            return 0

