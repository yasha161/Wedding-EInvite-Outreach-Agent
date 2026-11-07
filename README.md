# 💍 Wedding & Creative Service AI Outreach Suite

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Email Validation: DNS MX Verified](https://img.shields.io/badge/Validation-DNS%20MX%20Verified-brightgreen.svg)]()
[![TLS Security](https://img.shields.io/badge/Security-Gmail%20TLS%20587-orange.svg)]()
[![Anti-Spam](https://img.shields.io/badge/Pacing-Human%20Cadence-success.svg)]()

An autonomous, production-ready AI Outreach Suite containing two dedicated outreach engines:
1. **💍 Wedding & E-Invitation Agent** (`wedding_agent.py`) [ACTIVE]
   - Tailored specifically for **Luxury Wedding Planners, Event Management Agencies, E-Invitation Studios, and Wedding Cinematography Houses**.
2. **🎬 Creative Service Pitch Agent** (`service_pitch_agent.py`) [STANDBY / OFF BY DEFAULT]
   - Tailored for **Video Editing, Short-Form Reels/Shorts Retention Editing, and Podcast Clipping Agencies**.

---

## ⚡ Core Capabilities Across Both Agents

- 🎯 **Real-Time High-Intent Lead Scraping**:
  - Dynamically scrapes verified public contact details of active businesses and open hiring calls.
  - Excludes stale job seekers, bot accounts, and freelancer self-promotions.

- 🛡️ **Zero-Bounce Email Cleaning & DNS MX Validation**:
  - Automatic URL & suffix stripping (e.g. cleans typos like `name@gmail.comlet` -> `name@gmail.com`).
  - Strict Top-Level Domain (TLD) filtering.
  - **Live DNS MX Verification**: Resolves mail exchange server records in real-time before sending to prevent hard bounces and protect your sender reputation.

- 📱 **Instant Phone / WhatsApp Discovery & Telegram Alerts**:
  - Extracts 10-digit Indian (+91) and international (+1/UK) phone numbers directly from profiles and portfolios.
  - Automatically pushes warm lead profiles and phone numbers directly to your private **Telegram** bot for high-priority WhatsApp follow-ups.

- 🎬 **Rich 3D/Motion Video Attachment**:
  - Automatically compresses and attaches your luxury motion video invite sample (under Gmail's 25 MB limit) directly to the email body.

- 🕒 **Anti-Spam Pacing & Safety Guardrails**:
  - Random 45–75 second delay between dispatches.
  - Quota limits (10–15 leads per run).

---

## 📂 Project Architecture

```
Wedding-EInvite-Outreach-Agent/
│
├── leads/
│   ├── wedding_leads.csv           # Detailed lead log for Wedding outreach
│   ├── wedding_sent_history.json   # Deduplication database for Wedding outreach
│   ├── service_leads.csv           # Detailed lead log for Creative Service outreach
│   └── service_sent_history.json   # Deduplication database for Creative Service outreach
│
├── resources/
│   └── wedding_e_invite_sample.mp4 # Video sample (<25 MB) attached to wedding pitches
│
├── templates/
│   ├── __init__.py
│   └── pitch_templates.py          # High-converting B2B copy for Planners & Cinematographers
│
├── .env.example                    # Template for Gmail & Telegram credentials
├── .gitignore                      # Securely ignores secrets and heavy binaries
├── requirements.txt                # Lightweight dependencies (requests, dnspython, ddgs, etc.)
├── wedding_agent.py                # Main Wedding & E-Invite outreach engine
├── service_pitch_agent.py          # Creative Service (Video Editing/Reels) outreach engine (OFF by default)
├── LICENSE                         # MIT License
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
# SENDER CREDENTIALS (GMAIL SMTP TLS)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
SENDER_NAME="Your Name"

# TELEGRAM NOTIFICATIONS
TELEGRAM_BOT_TOKEN=
TELEGRAM_USER_ID=

# CREATIVE SERVICE AGENT SWITCH (Standby / Off by default)
SERVICE_PITCH_ENABLED=false
```

---

## ☁️ 24/7 Cloud Automation (GitHub Actions — Runs When PC is OFF)

This engine is equipped with native GitHub Actions workflows located in `.github/workflows/outreach_scheduler.yml`. Even when your local computer is powered off or disconnected, GitHub's cloud runners will execute your daily batches at optimal local business hours:

| Batch Segment | Trigger Time (IST) | Target Audience |
| :--- | :--- | :--- |
| **Morning Batch** | `10:00 AM IST` (`04:30 AM UTC`) | Luxury Wedding Planners across India & South Asia |
| **Afternoon Batch** | `02:30 PM IST` (`09:00 AM UTC`) | Dubai, UAE, UK & European Destination Agencies |
| **Night Batch** | `08:00 PM IST` (`02:30 PM UTC`) | USA, Canada & Global NRI Wedding Planners |

### How It Operates in the Cloud:
1. **Pulls from Pre-Queued Lead Pool**: If leads are pre-populated in `leads/wedding_leads.csv` with `QUEUED` status, the cloud runner consumes them immediately.
2. **Live Fallback Scraping**: If the pre-queued pool is empty, the runner automatically scrapes fresh live signals.
3. **DNS MX Verification**: Resolves mail exchange servers live before sending to prevent bounces.
4. **Attaches Video Sample**: The `resources/wedding_e_invite_sample.mp4` video (14.8 MB) is attached directly over Gmail TLS.
5. **Instant Telegram Alerts**: Sends warm lead alerts & client phone numbers to your Telegram bot in real time.
6. **Automatic Git History Commit**: Automatically commits back updated CSV statuses and `wedding_sent_history.json` to prevent ever emailing the same brand twice.

---

## 💍 Agent 1: Wedding & E-Invitation Agent (`wedding_agent.py`)

### 🔍 Dry Run (Safe Test Mode)
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

---

## 🎬 Agent 2: Creative Service Pitch Agent (`service_pitch_agent.py`)

> [!NOTE]
> **Standby Mode / Off by Default**: By default, running `python service_pitch_agent.py` will not execute or send any emails. It remains paused until you explicitly activate it.

### How to Activate When Ready:

#### Option A: Run via CLI Flag (One-Time Run)
```bash
# Safe dry-run test
python service_pitch_agent.py --activate --dry-run

# Live dispatch (Sends emails with human pacing)
python service_pitch_agent.py --activate --send --max 10
```

#### Option B: Enable Permanently via `.env`
Set in `.env`:
```ini
SERVICE_PITCH_ENABLED=true
```
Then run normally:
```bash
python service_pitch_agent.py --send --max 10
```

---

## 🛡️ Anti-Spam & Deliverability Standards

1. **DNS MX Record Resolution**: Ensures recipient server actually accepts incoming mail.
2. **Random Humanized Delays**: 45 to 75 seconds between consecutive emails to mimic human behavior.
3. **Daily Quotas**: Strict limit of 10-15 emails per session to maintain 100% Google mailbox health and zero domain blacklisting.
4. **History Deduplication**: JSON logs guarantee you never email the same contact twice.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
