# 💍 Wedding & E-Invitation AI Outreach Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Email Validation: DNS MX Verified](https://img.shields.io/badge/Validation-DNS%20MX%20Verified-brightgreen.svg)]()
[![TLS Security](https://img.shields.io/badge/Security-Gmail%20TLS%20587-orange.svg)]()
[![Anti-Spam](https://img.shields.io/badge/Pacing-Human%20Cadence-success.svg)]()

An autonomous, production-ready AI Outreach Engine tailored specifically for **Luxury Wedding Planners, Event Management Agencies, E-Invitation Studios, and Wedding Cinematography Houses**.

Designed to find hyper-targeted, verified leads from real-time web signals, validate emails via DNS MX records, extract verified client contact numbers for instant Telegram alerts, and send personalized high-converting video pitches with zero spam bounce.

---

## ⚡ Core Capabilities

- 🎯 **Real-Time High-Intent Lead Scraping**:
  - Dynamically scrapes verified public contact details of active wedding planners and luxury coordinators across India, UAE/Dubai, the UK, Europe, and the US/Canada.
  - Excludes stale job seekers, bot accounts, and spam directories.

- 🛡️ **Zero-Bounce Email Cleaning & DNS MX Validation**:
  - Automatic URL & suffix stripping (e.g. cleans typos like `name@gmail.comlet` -> `name@gmail.com`).
  - Strict Top-Level Domain (TLD) filtering.
  - **Live DNS MX Verification**: Resolves mail exchange server records in real-time before sending to prevent hard bounces and protect your sender reputation.

- 📱 **Instant Phone / WhatsApp Discovery & Telegram Alerts**:
  - Extracts 10-digit Indian (+91) and international (+1/UK) phone numbers directly from profiles and portfolios.
  - Automatically pushes warm lead profiles and phone numbers directly to your private **Telegram** bot for high-priority WhatsApp follow-ups.

- 🎬 **Rich 3D/Motion Video Attachment**:
  - Automatically compresses and attaches your luxury motion wedding invite video sample (under Gmail's 25 MB limit) directly to the email body.
  - Supports automatic fallback to hosted high-definition portfolio links if no local video file is present.

- 🕒 **Segmented 3-Tier Daily Batches (15 Leads / Session)**:
  - **Morning Batch (09:00 - 11:30 AM)**: India & South Asia luxury wedding planners (Delhi, Mumbai, Jaipur, Udaipur).
  - **Afternoon Batch (02:00 - 04:30 PM)**: Dubai, UAE, UK & European destination wedding agencies.
  - **Night Batch (08:30 - 10:30 PM)**: US, Canada & Global NRI wedding management companies.
  - Strict anti-spam pacing: random 45–75 second delay between dispatches.

- 🧪 **Safety & Dry-Run Mode**:
  - Test lead extraction, cleaning, and pitch formatting without sending a single email or consuming quota using the `--dry-run` flag.

---

## 📂 Project Architecture

```
Wedding-EInvite-Outreach-Agent/
│
├── leads/
│   ├── wedding_leads.csv           # Detailed lead log (Brand, Email, Phone, Status, Timestamp)
│   └── wedding_sent_history.json   # Deduplication database to prevent double-contacting
│
├── resources/
│   └── wedding_e_invite_sample.mp4 # Video sample (<25 MB) attached to pitches
│
├── templates/
│   ├── __init__.py
│   └── pitch_templates.py          # High-converting B2B copy for Planners & Cinematographers
│
├── .env.example                    # Template for Gmail & Telegram credentials
├── .gitignore                      # Securely ignores secrets and heavy binaries
├── requirements.txt                # Lightweight dependencies (requests, dnspython, ddgs, etc.)
├── wedding_agent.py                # Main orchestration and dispatch engine
└── README.md                       # Documentation and usage guide
```

---

## 🚀 Quickstart Guide

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/yasha161/Wedding-EInvite-Outreach-Agent.git
cd Wedding-EInvite-Outreach-Agent

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```ini
# ==============================================================================
# SENDER CREDENTIALS (GMAIL SMTP TLS)
# ==============================================================================
# Generate your 16-character Google App Password:
# https://myaccount.google.com/apppasswords
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
SENDER_NAME="Your Name"

# ==============================================================================
# TELEGRAM NOTIFICATIONS (OPTIONAL BUT RECOMMENDED)
# ==============================================================================
# Create a bot via @BotFather and retrieve chat ID via @userinfobot
TELEGRAM_BOT_TOKEN=
TELEGRAM_USER_ID=

# ==============================================================================
# AGENT SAFETY LIMITS
# ==============================================================================
MIN_DELAY_SECONDS=45
MAX_DELAY_SECONDS=75
DEFAULT_BATCH_MAX=15
```

### 3. Add Video Sample (Optional)

Drop your compressed motion video invite (`< 25 MB`) inside the `resources/` folder:
```
resources/wedding_e_invite_sample.mp4
```
*Note: If no file is placed here, the agent automatically inserts high-converting portfolio drive links into the email body without failing.*

---

## 🛠️ Usage & Commands

### 🔍 Dry Run (Safe Test Mode)
Scrapes, cleans, and generates pitches without sending actual emails:
```bash
python wedding_agent.py --dry-run
```

### 🌅 Run Specific Daily Batches

#### 1. Morning Batch (India & South Asia):
```bash
python wedding_agent.py --batch morning --max 15 --send
```

#### 2. Afternoon Batch (Dubai, UAE & UK Destination Planners):
```bash
python wedding_agent.py --batch afternoon --max 15 --send
```

#### 3. Night Batch (USA, Canada & NRI Planners):
```bash
python wedding_agent.py --batch night --max 15 --send
```

### 📊 Inspecting Leads & Sent Logs

All extracted and contacted leads are saved to `leads/wedding_leads.csv`:
```csv
brand_name,email,phone,batch,target_region,service_pitched,subject,status,timestamp
Royal Weddings Delhi,contact@royalweddings.in,+919876543210,morning,India,E-Invitation,Collab on 3D Motion Invites,SENT,2026-11-06 10:15:22
```

---

## 📬 High-Converting Pitch Architecture

The engine uses tailored, non-salesy B2B templates designed for agency decision makers:

1. **For Wedding Planners**: Focuses on white-label 3D & motion invitation cards that impress their high-ticket brides and grooms without adding overhead to their team.
2. **For Wedding Cinematographers**: Focuses on teaser reels, aesthetic typography intro videos, and cinematic save-the-date graphics.

---

## 🛡️ Anti-Spam & Deliverability Standards

1. **DNS MX Record Resolution**: Ensures recipient server actually accepts incoming mail.
2. **Random Humanized Delays**: 45 to 75 seconds between consecutive emails to mimic human behavior.
3. **Daily Quotas**: Strict limit of 15 emails per session (max 45/day) to maintain 100% Google mailbox health and zero domain blacklisting.
4. **History Deduplication**: `leads/wedding_sent_history.json` guarantees you never email the same contact twice.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
