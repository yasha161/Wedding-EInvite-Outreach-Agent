"""
=============================================================================
CREATIVE SERVICE PITCH AGENT (VIDEO EDITING, REELS & PODCAST PRODUCTION)
=============================================================================
Autonomous Lead Scraper, Validator & High-Converting Pitch Dispatcher for:
- Video Editing & High-Retention Short-Form Reels
- Podcast Audio/Video Clipping & Repurposing
- YouTube Long-Form Storytelling & Motion Graphics

STATUS: PAUSED / OFF BY DEFAULT (Activate when ready via flag or .env)
=============================================================================
"""

import sys
import os
import re
import csv
import json
import time
import random
import smtplib
import argparse
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import dns.resolver
from dotenv import load_dotenv

# Windows non-interactive encoding fix
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# MASTER SAFETY TOGGLE: PAUSED / OFF BY DEFAULT
# ==============================================================================
# Set SERVICE_PITCH_ENABLED=true in .env OR pass --activate CLI flag to enable.
AGENT_ACTIVE_CONFIG = os.getenv("SERVICE_PITCH_ENABLED", "false").lower() in ("true", "1", "yes")

# Credentials & Sender Information
GMAIL_USER = os.getenv("GMAIL_USER") or os.getenv("GMAIL_ADDRESS") or ""
GMAIL_APP_PASSWORD = (os.getenv("GMAIL_APP_PASSWORD") or "").replace(" ", "")
SENDER_NAME = os.getenv("SENDER_NAME", "Yash")

# Telegram Bot Integration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or ""
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID") or ""

# Rate Limiting & Quotas
MIN_DELAY_SECONDS = int(os.getenv("MIN_DELAY_SECONDS", 45))
MAX_DELAY_SECONDS = int(os.getenv("MAX_DELAY_SECONDS", 75))
DEFAULT_BATCH_MAX = int(os.getenv("DEFAULT_BATCH_MAX", 10))

# Directories & Files
LEADS_DIR = BASE_DIR / "leads"
SERVICE_CSV = LEADS_DIR / "service_leads.csv"
SERVICE_HISTORY = LEADS_DIR / "service_sent_history.json"
LEADS_DIR.mkdir(parents=True, exist_ok=True)

# Strict Validation Regex Patterns
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b|(?:\+?91[\-\s]?)?[6-9]\d{9}\b|(?:\+?1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}\b')

VALID_TLDS = {'com', 'in', 'co', 'io', 'ai', 'org', 'net', 'media', 'agency', 'studio', 'tech', 'tv', 'uk', 'de', 'ca', 'me'}

EXCLUDED_DOMAINS = {
    'example.com', 'domain.com', 'wixpress.com', 'shopify.com',
    'wordpress.org', 'cloudflare.com', 'google.com', 'microsoft.com',
    'apple.com', 'facebook.com', 'twitter.com', 'x.com', 'instagram.com',
    'youtube.com', 'tiktok.com', 'linkedin.com', 'github.com'
}

EXCLUDED_USERS = {
    'sentry', 'noreply', 'no-reply', 'abuse', 'privacy', 'support',
    'help', 'admin', 'billing', 'jobs-noreply', 'donotreply'
}

FREELANCER_PHRASES = [
    'for hire', '[for hire]', 'i am a video editor', 'i am looking for work',
    'dm me to hire', 'check out my portfolio', 'my rates are', 'freelancer available',
    'open for commissions', 'editor for hire', 'hire me'
]

HIRING_SIGNALS = [
    'hiring video editor', 'hiring reels editor', 'looking for video editor',
    'looking for podcast editor', 'hiring short form editor', 'editor needed',
    'need a video editor', 'send portfolio to', 'send your resume to'
]

# High-Intent Discovery Queries
SERVICE_QUERIES = [
    'site:instagram.com "hiring video editor" "gmail.com"',
    'site:instagram.com "looking for video editor" "gmail.com"',
    'site:instagram.com "hiring reels editor" "gmail.com"',
    'site:instagram.com "podcast editor" "send portfolio" "gmail.com"',
    'site:instagram.com "hiring motion designer" "gmail.com"',
    'site:twitter.com "hiring video editor" "gmail.com"',
    'site:twitter.com "looking for a video editor" email gmail.com'
]

def send_telegram(text: str):
    """Dispatches lead alerts to user's Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_USER_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id": TELEGRAM_USER_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }, timeout=10)
    except Exception as e:
        print(f"[!] Telegram alert error: {e}", flush=True)

def load_sent_history() -> set:
    if not SERVICE_HISTORY.exists():
        return set()
    try:
        with open(SERVICE_HISTORY, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {item.get('email', '').strip().lower() for item in data if item.get('email')}
    except Exception:
        return set()

def record_sent_lead(record: dict):
    history = []
    if SERVICE_HISTORY.exists():
        try:
            with open(SERVICE_HISTORY, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(record)
    with open(SERVICE_HISTORY, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

def save_lead_to_csv(lead: dict):
    file_exists = SERVICE_CSV.exists()
    fieldnames = [
        "brand_name", "email", "phone", "service_type",
        "subject", "source_link", "status", "timestamp"
    ]
    with open(SERVICE_CSV, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "brand_name": lead.get("brand_name", ""),
            "email": lead.get("email", ""),
            "phone": lead.get("phone", ""),
            "service_type": lead.get("service_type", ""),
            "subject": lead.get("subject", ""),
            "source_link": lead.get("source_link", ""),
            "status": lead.get("status", "QUEUED"),
            "timestamp": lead.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        })

def clean_email(email_str: str) -> str:
    """Strips accidental punctuation, URLs, and trailing typos like gmail.comlet."""
    cleaned = email_str.lower().strip().rstrip('.,;:()[]{}<>"\'')
    if '@gmail.com' in cleaned:
        idx = cleaned.find('@gmail.com')
        return cleaned[:idx + 10]
    m = re.search(r'([a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z]{2,6}))', cleaned)
    if m:
        return m.group(1)
    return ""

def is_valid_email(email: str) -> bool:
    """Enforces strict syntax, domain blacklist, and live DNS MX resolution."""
    if not email or '@' not in email:
        return False
    user, domain = email.split('@', 1)
    if len(user) < 3 or user.isdigit():
        return False
    if domain in EXCLUDED_DOMAINS or user in EXCLUDED_USERS:
        return False
    tld = domain.split('.')[-1]
    if tld not in VALID_TLDS:
        return False
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=3)
        if not answers:
            return False
    except Exception:
        return False
    return True

def extract_phone_numbers(text: str) -> list:
    found = PHONE_REGEX.findall(text)
    cleaned = []
    for ph in found:
        p = ph.strip()
        if len(re.sub(r'\D', '', p)) >= 10:
            cleaned.append(p)
    return list(set(cleaned))

def clean_brand_name(raw_title: str, email: str) -> str:
    m = re.search(r'\bat\s+([A-Za-z0-9\s\'\&]+?)(?:\s*\||\s*\-|\s*•|\s*\.\.\.|$)', raw_title, flags=re.IGNORECASE)
    if m:
        cand = m.group(1).strip()
        if len(cand) >= 3 and len(cand) <= 30 and cand.lower() not in {'youtube', 'instagram', 'facebook'}:
            return cand.title()

    cleaned = raw_title.split('|')[0].split('•')[0].split('-')[0].split(':')[0].strip()
    cleaned = re.sub(r'(@|Instagram|on Instagram|YouTube|Twitter|X|Facebook|TikTok)', '', cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'[\(\)\[\]\{\}\<\>•\-:|]', ' ', cleaned).strip()
    words = [w for w in cleaned.split() if len(w) > 1 and not w.isdigit()]
    candidate = " ".join(words[:2])

    invalid = {'there', 'team', 'contact', 'admin', 'help', 'jobs', 'official', 'editor', 'video'}
    if len(candidate) >= 3 and len(candidate) <= 30 and candidate.lower() not in invalid:
        return candidate.title()

    user = email.split('@')[0].lower()
    for prefix in ['reach', 'team', 'contact', 'info', 'business', 'official', 'the', 'workwith']:
        if user.startswith(prefix) and len(user) > len(prefix) + 2:
            user = user[len(prefix):]
    user = user.replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
    parts = [w.capitalize() for w in user.split() if not w.isdigit() and len(w) > 1]
    if parts:
        cand_user = " ".join(parts[:2])
        if cand_user.lower() not in invalid:
            return cand_user

    return "there"

def is_genuine_hiring(text: str) -> bool:
    lower = text.lower()
    for phrase in FREELANCER_PHRASES:
        if phrase in lower:
            return False
    return any(sig in lower for sig in HIRING_SIGNALS)

def build_service_pitch(brand_name: str, snippet: str) -> tuple[str, str, str]:
    """Generates personalized service pitch for video editing, reels, or podcast clipping."""
    lower = snippet.lower()
    greeting = f"Hey {brand_name}," if brand_name.lower() != "there" else "Hey there,"

    if "podcast" in lower or "interview" in lower:
        subject = f"Quick sample cut for your podcast, {brand_name}" if brand_name.lower() != "there" else "Quick sample cut for your podcast"
        service_type = "Podcast & Long-Form Video Clipping"
        body = f"""{greeting}

Saw your recent post looking for an editor to handle your podcast and long-form video content.

I specialize in extracting the most engaging 30–45s moments from long-form episodes and transforming them into retention-optimized vertical reels (punchy dynamic captions, B-roll overlays, and crisp sound design) engineered specifically for YouTube Shorts and Instagram Reels.

I would love to edit 1 free sample clip from your latest episode with zero obligations so you can review our pacing and quality firsthand.

Mind if I send the sample clip over once it is rendered?

Best,
{SENDER_NAME}"""

    elif "reels" in lower or "short" in lower or "tiktok" in lower:
        subject = f"Video editor for your reels, {brand_name}" if brand_name.lower() != "there" else "Video editor for your reels"
        service_type = "Short-Form Retention & Reels Editing"
        body = f"""{greeting}

Saw your post regarding the open video editor role for short-form video content.

I specialize in high-retention vertical video editing—seamless jump-cuts, dynamic kinetic typography, and audio hooks designed to stop the scroll and drive maximum audience watch time.

I would love to cut 1 free sample reel tailored to your exact style so you can review our turnaround speed and polish with zero risk.

Would you be open to taking a look over email?

Best,
{SENDER_NAME}"""

    else:
        subject = f"Video editor role at {brand_name}" if brand_name.lower() != "there" else "Video editor role - sample clip idea"
        service_type = "YouTube & High-Retention Video Production"
        body = f"""{greeting}

Saw your post looking for a dedicated video editor.

I specialize in fast-turnaround, high-retention video production—crafting clean pacing, sound effects, motion graphics, and visual storytelling that hold viewer attention from frame 1.

I would love to produce 1 short sample edit tailored specifically for {brand_name} completely free of cost so you can judge how we work.

Mind if I share the sample preview once it is ready?

Best,
{SENDER_NAME}"""

    return subject, body, service_type

def send_email_tls(to_email: str, subject: str, body: str) -> bool:
    """Dispatches email safely via Gmail TLS 587."""
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("[!] ERROR: GMAIL_USER or GMAIL_APP_PASSWORD missing in .env")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"{SENDER_NAME} <{GMAIL_USER}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=25)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"[!] SMTP dispatch failed for {to_email}: {e}")
        return False

def scrape_service_leads(max_leads: int = 10) -> list:
    """Scrapes fresh video editing hiring leads using DuckDuckGo HTML."""
    leads = []
    seen_emails = load_sent_history()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    random.shuffle(SERVICE_QUERIES)

    for q in SERVICE_QUERIES:
        if len(leads) >= max_leads:
            break
        print(f"\n[+] Searching: {q}")
        try:
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(q)}"
            resp = requests.get(url, headers=headers, timeout=12)
            if resp.status_code != 200:
                continue

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('div', class_='result')

            for r in results:
                if len(leads) >= max_leads:
                    break
                snippet_elem = r.find('a', class_='result__snippet')
                title_elem = r.find('a', class_='result__title')
                snippet = snippet_elem.get_text() if snippet_elem else ""
                title = title_elem.get_text() if title_elem else ""
                full_text = f"{title} {snippet}"

                # Match email
                raw_emails = EMAIL_REGEX.findall(full_text)
                for raw in raw_emails:
                    email = clean_email(raw)
                    if not email or email in seen_emails or not is_valid_email(email):
                        continue

                    # Filter out freelancer self-promotions
                    if not is_genuine_hiring(full_text):
                        continue

                    brand_name = clean_brand_name(title, email)
                    phone_numbers = extract_phone_numbers(full_text)
                    phone_str = phone_numbers[0] if phone_numbers else ""

                    subject, body, service_type = build_service_pitch(brand_name, full_text)

                    lead = {
                        "brand_name": brand_name,
                        "email": email,
                        "phone": phone_str,
                        "service_type": service_type,
                        "subject": subject,
                        "body": body,
                        "snippet": full_text[:180],
                        "source_link": r.find('a', class_='result__url')['href'] if r.find('a', class_='result__url') else ""
                    }
                    leads.append(lead)
                    seen_emails.add(email)
                    print(f"  ✓ Verified Lead Found: {brand_name} <{email}> | Phone: {phone_str or 'N/A'}")
                    break

            time.sleep(random.uniform(2.5, 4.5))
        except Exception as e:
            print(f"  [!] Query error: {e}")
            continue

    return leads

def main():
    parser = argparse.ArgumentParser(description="Creative Service Pitch Agent (Video Editing / Reels / Podcasts)")
    parser.add_argument("--activate", action="store_true", help="Explicitly activate the agent for this execution")
    parser.add_argument("--send", action="store_true", help="Send actual emails (otherwise dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate scraping and pitch generation without sending")
    parser.add_argument("--max", type=int, default=DEFAULT_BATCH_MAX, help="Max emails to process")
    args = parser.parse_args()

    # Master Guard: Check if agent is enabled
    is_active = AGENT_ACTIVE_CONFIG or args.activate

    print("\n" + "=" * 70)
    print("🎬 CREATIVE SERVICE PITCH AGENT (VIDEO EDITING & REELS OUTREACH)")
    print("=" * 70)

    if not is_active:
        print("\n⏸️  STATUS: AGENT IS CURRENTLY PAUSED / OFF")
        print("----------------------------------------------------------------------")
        print("Aapne is agent ko OFF rakhne ko kaha tha, isliye ye standby par hai.")
        print("Jab aapko ise chalana ho, simply:")
        print("  1. CLI se run karein:   python service_pitch_agent.py --activate --dry-run")
        print("  2. Ya live mail bhein:  python service_pitch_agent.py --activate --send")
        print("  3. Ya .env file me set karein: SERVICE_PITCH_ENABLED=true")
        print("----------------------------------------------------------------------\n")
        return

    print(f"[*] Agent Status: ACTIVE")
    print(f"[*] Mode: {'LIVE DISPATCH (SMTP)' if (args.send and not args.dry-run) else 'DRY RUN (Safe Simulation)'}")
    print(f"[*] Max Quota: {args.max} leads")
    print("=" * 70)

    leads = scrape_service_leads(max_leads=args.max)
    print(f"\n[+] Total verified high-intent leads scraped: {len(leads)}")

    if not leads:
        print("[!] No new leads found matching strict hiring filters at this time.")
        return

    sent_count = 0
    for i, lead in enumerate(leads, 1):
        print(f"\n--- [{i}/{len(leads)}] Pitching: {lead['brand_name']} ({lead['email']}) ---")
        print(f"Service Type : {lead['service_type']}")
        print(f"Phone/WhatsApp : {lead['phone'] or 'None found'}")
        print(f"Subject      : {lead['subject']}")

        if args.dry_run or not args.send:
            print("[DRY-RUN] Previewing Pitch Body:")
            print("-" * 40)
            print(lead['body'])
            print("-" * 40)
            lead['status'] = 'DRY_RUN'
            save_lead_to_csv(lead)
        else:
            print("[SMTP] Dispatching email via Gmail TLS...")
            success = send_email_tls(lead['email'], lead['subject'], lead['body'])
            if success:
                lead['status'] = 'SENT'
                save_lead_to_csv(lead)
                record_sent_lead({
                    "brand_name": lead['brand_name'],
                    "email": lead['email'],
                    "phone": lead['phone'],
                    "service_type": lead['service_type'],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                sent_count += 1
                print(f"  ✓ Successfully sent to {lead['email']}")

                # Instant Telegram alert
                tg_msg = (
                    f"🎯 *New Service Pitch Sent!* [Batch: Video Editor]\n"
                    f"🏢 *Client*: `{lead['brand_name']}`\n"
                    f"✉️ *Email*: `{lead['email']}`\n"
                    f"📱 *Phone*: `{lead['phone'] or 'N/A'}`\n"
                    f"🎬 *Pitch*: `{lead['service_type']}`\n"
                    f"⏰ *Time*: {time.strftime('%H:%M:%S')}"
                )
                send_telegram(tg_msg)

                if i < len(leads):
                    delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                    print(f"[*] Anti-spam sleep for {delay:.1f}s...")
                    time.sleep(delay)
            else:
                lead['status'] = 'FAILED'
                save_lead_to_csv(lead)

    print("\n" + "=" * 70)
    print(f"✅ Run Completed! Emails Sent: {sent_count} / Processed: {len(leads)}")
    print(f"📁 Log saved to: {SERVICE_CSV}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
