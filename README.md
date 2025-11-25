# LinkedIn Bulk Profile Scraper v2.0

**Enterprise-Grade LinkedIn Profile Scraper with Anti-Detection & Multi-Agent Architecture**

> ⚠️ **DISCLAIMER**: This tool violates LinkedIn's Terms of Service. Use for educational purposes only!

## 🎯 Features

- ✅ **Bulk Profile Scraping** - Search & scrape hundreds of profiles automatically
- ✅ **Text-Based Extraction** - Extracts by content (resistant to HTML changes)
- ✅ **Multi-Agent System** - SearchAgent, ScrapeAgent, ValidationAgent working together
- ✅ **Resume Capability** - SQLite database tracks progress, resume anytime
- ✅ **No Duplicates** - Intelligent deduplication prevents re-scraping
- ✅ **Anti-Detection** - 10+ layers of human-like behavior & fingerprint spoofing:
  - User-Agent randomization
  - Viewport/timezone/locale spoofing
  - Natural scrolling & mouse movements
  - Human-like typing with delays
  - Adaptive rate limiting
  - Modal dialog handling
- ✅ **Multi-Format Export** - JSON, CSV, Excel with statistics
- ✅ **Data Validation** - Completeness scoring & quality checks
- ✅ **CAPTCHA Detection** - Alerts when manual intervention needed

## 🚀 Quick Start

### 1. Setup

```powershell
# Activate virtual environment
.\linkedin_env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure Credentials

Edit `.env`:
```
LINKEDIN_EMAIL=your_email@gmail.com
LINKEDIN_PASSWORD=your_password
```

### 3. Run

```powershell
# Activate environment
.\linkedin_env\Scripts\Activate.ps1

# Run scraper
python main.py

# Follow interactive menu:
# 1. Search & Scrape (new batch)
# 2. Resume Previous (continue from checkpoint)
# 3. Export Data (download results)
# 4. View Statistics (progress & completeness)
# 5. Cleanup Old Data (delete old entries)
```

## 📁 Project Structure

```
├── main.py                    # Entry point (interactive CLI)
├── requirements.txt           # Dependencies
├── .env                      # Credentials (create this)
├── README.md                 # This file
│
├── agents/                   # Multi-agent system
│   ├── search_agent.py       # LinkedIn search automation
│   ├── scrape_agent.py       # Profile data extraction
│   └── validation_agent.py   # Data quality validation
│
├── scraper/                  # Core scraping engine
│   ├── browser_controller.py # Playwright browser management
│   ├── data_extractor.py     # Text-based data parsing
│   └── human_behavior.py     # Anti-detection behaviors
│
├── database/                 # Data persistence
│   └── db_manager.py         # SQLite database interface
│
├── utils/                    # Utilities
│   ├── config.py             # Configuration management
│   ├── logger_setup.py       # Logging configuration
│   └── export.py             # Multi-format export
│
├── config/                   # Configuration files
│   └── settings.yaml
│
├── data/                     # Runtime data
│   ├── linkedin_scraper.db   # SQLite database (auto-created)
│   ├── exports/              # Exported files (JSON/CSV/Excel)
│   └── screenshots/          # Debug screenshots (on errors)
│
├── logs/                     # Application logs
│   └── scraper.log
│
├── ARCHIVE/                  # Old test files (reference only)
│   └── ... (debug/test scripts)
│
└── linkedin_env/             # Python virtual environment
```

## 🔧 How It Works

### Architecture

```
User Input (interactive menu)
    ↓
┌─────────────────────────────────┐
│  CLI Interface (main.py)        │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Multi-Agent Workflow           │
├─────────────────────────────────┤
│ 1. SearchAgent                  │
│    - Searches LinkedIn          │
│    - Extracts profile URLs      │
│                                 │
│ 2. ScrapeAgent                  │
│    - Navigates to profiles      │
│    - Handles modals & blocks    │
│    - Extracts profile data      │
│                                 │
│ 3. ValidationAgent              │
│    - Scores completeness        │
│    - Validates data quality     │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Data Storage & Export          │
│  - SQLite Database              │
│  - JSON/CSV/Excel Export        │
└─────────────────────────────────┘
```

## 📊 Data Extracted (Per Profile)

- Full name & headline
- Current/past companies
- Job titles & employment dates
- Location
- Skills (with endorsement counts)
- Certifications & education
- About/Summary section
- Website & social links
- Completeness score (0-100%)

## 🗄️ Database

SQLite database tracks:
- Profile URLs & scraped data
- Scraping progress (pending/completed/failed)
- Error logs & retry counts
- Data completeness scores
- Timestamps for tracking

## ⚡ Performance

- ~2-5 profiles per minute (respecting rate limits)
- Intelligent delays increase with progress (anti-detection)
- Can scrape 100s of profiles in one session
- Resume capability allows multi-day operations
- Automatic retry on failures (max 3 attempts)

## 🔒 Anti-Detection (10+ Layers)

1. **User-Agent rotation** - 10+ browser variants
2. **Viewport/timezone/locale spoofing** - Looks like different locations
3. **Stealth JavaScript injections** - Removes automation indicators
4. **Natural scrolling & mouse movements** - Human-like behavior
5. **Adaptive rate limiting** - Delays increase as progress increases
6. **Modal dialog closing** - Handles LinkedIn popups
7. **CAPTCHA detection** - Alerts for manual solving
8. **Connection pooling** - Reduces detection patterns
9. **CancelledError handling** - Graceful cleanup
10. **IP rotation ready** - Proxy support built-in

## ⚙️ Configuration

Edit `config/settings.yaml`:

```yaml
scraping:
  headless: False              # Show browser window
  max_profiles_per_search: 100
  delay_between_profiles: [15, 30]  # Random seconds
  use_stealth: True
  timeout: 60000               # milliseconds
  max_retries: 3
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No profiles found" | Check internet, LinkedIn credentials, different query |
| "Navigation timeout" | Increase timeout in config, check anti-bot status |
| "Profile access restricted" | Normal (privacy settings), try different profiles |
| "Database locked" | Close other Python instances, restart program |
| Slow scraping | Respect LinkedIn rate limits, normal behavior |

## 📝 Output Example

**profiles.json**:
```json
{
  "name": "John Doe",
  "headline": "Senior Software Engineer",
  "current_company": "Tech Corp",
  "skills": ["Python", "JavaScript", "React"],
  "completeness": 85,
  "profile_url": "https://linkedin.com/in/johndoe"
}
```

## 📦 Requirements

- Python 3.8+
- Playwright (browser automation)
- pandas (Excel export)
- PyYAML (config management)

Install all: `pip install -r requirements.txt`

## 🔐 Security

- Credentials in `.env` (never commit!)
- Local SQLite database only
- No external data transmission
- Screenshots only on errors (debugging)

## ⚖️ Legal & Ethical

- **Educational Use Only** - Respect LinkedIn Terms of Service
- **Rate Limiting** - Scrape responsibly
- **Data Privacy** - Use collected data ethically
- **Account Safety** - Use test/secondary accounts
- **Legal Compliance** - Check local laws first

## ✅ Current Status

- ✅ Core scraping functional
- ✅ Anti-detection implemented
- ✅ Database persistence working
- ✅ Multi-format export operational
- ✅ Resume capability active
- ⚠️ LinkedIn actively blocking (use VPN/rotate accounts)

---

**Made for learning. Not affiliated with LinkedIn.**
