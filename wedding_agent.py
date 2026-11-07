"""
=============================================================================
WEDDING & E-INVITATION AI OUTREACH AGENT
=============================================================================
Autonomous Lead Scraper, Validator & High-Converting Pitch Dispatcher for:
- Wedding Planners & Event Management Agencies
- Luxury Invitation Designers & E-Invite Studios
- Wedding Cinematography & Photography Houses

Features:
- Live web & social signal discovery (Instagram, Google, regional directories).
- DNS MX record & strict syntax verification (Zero-Bounce Guarantee).
- Automatic Phone / WhatsApp number extraction with instant Telegram alerts.
- Attaches compressed 3D/Motion video invites under Gmail's 25 MB limit.
- 15 leads per batch (Morning, Afternoon, Night = 45 leads/day).
- Full anti-spam pacing with natural delays (45-75s) and safe dry-run mode.
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
from email.mime.base import MIMEBase
from email import encoders
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

from templates.pitch_templates import get_wedding_planner_pitch, get_wedding_cinema_pitch

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

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
DEFAULT_BATCH_MAX = int(os.getenv("DEFAULT_BATCH_MAX", 15))

# Directories & Files
LEADS_DIR = BASE_DIR / "leads"
WEDDING_CSV = LEADS_DIR / "wedding_leads.csv"
WEDDING_HISTORY = LEADS_DIR / "wedding_sent_history.json"
RESOURCE_DIR = BASE_DIR / "resources"
SAMPLE_VIDEO_PATH = RESOURCE_DIR / "wedding_e_invite_sample.mp4"
LEADS_DIR.mkdir(parents=True, exist_ok=True)
RESOURCE_DIR.mkdir(parents=True, exist_ok=True)

# Strict Regex Patterns
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?91[\-\s]?)?[6-9]\d{4}[\-\s]?\d{5}\b|(?:\+?91[\-\s]?)?[6-9]\d{9}\b|(?:\+?1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}\b')

VALID_TLDS = {'com', 'in', 'co', 'io', 'ai', 'org', 'net', 'media', 'agency', 'studio', 'tech', 'tv', 'uk', 'de', 'ca', 'me', 'club'}

EXCLUDED_DOMAINS = {
    'example.com', 'domain.com', 'wixpress.com', 'shopify.com',
    'wordpress.org', 'cloudflare.com', 'google.com', 'microsoft.com',
    'apple.com', 'facebook.com', 'twitter.com', 'x.com', 'instagram.com',
    'youtube.com', 'tiktok.com', 'linkedin.com', 'github.com', 'pinterest.com'
}

EXCLUDED_USERS = {
    'sentry', 'noreply', 'no-reply', 'abuse', 'privacy', 'support',
    'help', 'admin', 'billing', 'jobs-noreply', 'donotreply',
    'production', 'info', 'contact', 'team', 'hello', 'booking', 'bookings',
    'office', 'enquiry', 'inquiry', 'general', 'press', 'marketing', 'sales',
    'orders', 'jobs', 'career', 'careers', 'hr', 'studio', 'media', 'mail',
    'pr', 'service', 'services', 'work', 'collab', 'collaboration', 'official',
    'business', 'event', 'wedding'
}

REJECT_VENDORS = [
    'makeup', 'mua', 'hairstylist', 'hair stylist', 'food', 'foodie', 'restaurant',
    'cafe', 'cake', 'bakery', 'mehndi', 'mehendi', 'henna', 'florist', 'floral',
    'jewellery', 'jewelry', 'dj', 'catering', 'caterer', 'bartender', 'dress',
    'trousseau', 'decor only', 'decorator only'
]

REQUIRED_ROLES = [
    'wedding planner', 'wedding planning', 'wedding design', 'event planner',
    'event management', 'wedding management', 'luxury wedding', 'destination wedding',
    'wedding invitation', 'wedding invites', 'e-invite', 'invitation designer',
    'wedding film', 'wedding cinema', 'wedding cinematography'
]

DEAD_EMAIL_BLACKLIST = {
    'sweetweddingplanner@gmail.com', 'videosmakeupbymelinn@gmail.com',
    'production@gmail.com', 'torontofood85@gmail.com', 'makeupbymelinn@gmail.com',
    'productionthem@gmail.com', 'getzenny@gmail.com'
}

NEGATIVE_PHRASES = [
    'for hire', '[for hire]', 'i am a video editor', 'looking for a job',
    'resume attached', 'apply here for job', 'my portfolio'
]

# High-Intent Target Queries (2025/2026 Recency Guardrail)
BATCH_TARGETS = {
    "morning": {
        "name": "Morning Batch (India & South Asia Luxury Wedding Planners)",
        "geo": "India OR Delhi OR Mumbai OR Jaipur OR Udaipur",
        "queries": [
            'site:instagram.com "wedding planner" "gmail.com" "2025" OR "2026" Delhi OR Mumbai',
            'site:instagram.com "wedding planner" "gmail.com" "2025" OR "2026" Jaipur OR Udaipur',
            'site:instagram.com "wedding invitation" "gmail.com" "2025" OR "2026"',
            'site:instagram.com "destination wedding" "gmail.com" "2025" OR "2026" India',
            'site:instagram.com "luxury wedding planner" "gmail.com" "2025" India',
            'wedding planner "contact" "gmail.com" "2025" Delhi OR Mumbai'
        ]
    },
    "afternoon": {
        "name": "Afternoon Batch (UK, Dubai & European Destination Planners)",
        "geo": "Dubai OR UK OR London OR Europe",
        "queries": [
            'site:instagram.com "wedding planner" "gmail.com" "2025" OR "2026" Dubai',
            'site:instagram.com "luxury wedding" "gmail.com" "2025" OR "2026" UAE OR Dubai',
            'site:instagram.com "wedding planner" "gmail.com" "2025" OR "2026" London OR UK',
            'site:instagram.com "destination wedding planner" "gmail.com" "2025" OR "2026" Europe'
        ]
    },
    "night": {
        "name": "Night Batch (USA, Canada & NRI Wedding Coordinators)",
        "geo": "USA OR Canada",
        "queries": [
            'site:instagram.com "wedding planner" "gmail.com" "2025" OR "2026" USA',
            'site:instagram.com "indian wedding planner" "gmail.com" "2025" OR "2026" USA',
            'site:instagram.com "luxury wedding planner" "gmail.com" "2025" OR "2026" California OR New York',
            'site:instagram.com "wedding planner" "gmail.com" "2025" OR "2026" Canada OR Toronto'
        ]
    }
}

def send_telegram(text: str):
    """Dispatches markdown notifications to user's Telegram."""
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
        print(f"[!] Telegram error: {e}", flush=True)

def load_sent_history() -> set:
    if not WEDDING_HISTORY.exists():
        return set()
    try:
        with open(WEDDING_HISTORY, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {item.get('email', '').strip().lower() for item in data if item.get('email')}
    except Exception:
        return set()

def record_sent_lead(record: dict):
    history = []
    if WEDDING_HISTORY.exists():
        try:
            with open(WEDDING_HISTORY, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(record)
    with open(WEDDING_HISTORY, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

def save_lead_to_csv(lead: dict):
    file_exists = WEDDING_CSV.exists()
    fieldnames = [
        "brand_name", "email", "phone", "batch", "target_region",
        "service_pitched", "subject", "source_link", "status", "timestamp"
    ]
    with open(WEDDING_CSV, 'a', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "brand_name": lead.get("brand_name", ""),
            "email": lead.get("email", ""),
            "phone": lead.get("phone", ""),
            "batch": lead.get("batch", ""),
            "target_region": lead.get("target_region", ""),
            "service_pitched": lead.get("service_pitched", ""),
            "subject": lead.get("subject", ""),
            "source_link": lead.get("source_link", ""),
            "status": lead.get("status", "QUEUED"),
            "timestamp": lead.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
        })

def load_queued_leads_from_csv(batch_name: str) -> list:
    """Loads pre-queued leads from CSV for this batch that haven't been sent yet."""
    if not WEDDING_CSV.exists():
        return []
    sent_history = load_sent_history()
    queued = []
    try:
        with open(WEDDING_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                em = row.get("email", "").strip().lower()
                st = row.get("status", "").strip().upper()
                b = row.get("batch", "").strip().lower()
                if em and em not in sent_history and st.startswith("QUEUED") and (b == batch_name or not b):
                    queued.append(row)
    except Exception as e:
        print(f"[!] Error reading queued leads from CSV: {e}")
    return queued

def update_lead_status_in_csv(email: str, new_status: str):
    """Updates the status and timestamp of a lead in wedding_leads.csv."""
    if not WEDDING_CSV.exists():
        return
    rows = []
    fieldnames = [
        "brand_name", "email", "phone", "batch", "target_region",
        "service_pitched", "subject", "source_link", "status", "timestamp"
    ]
    try:
        with open(WEDDING_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                fieldnames = reader.fieldnames
            for row in reader:
                if row.get("email", "").strip().lower() == email.strip().lower():
                    row["status"] = new_status
                    row["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
                rows.append(row)
        with open(WEDDING_CSV, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except Exception as e:
        print(f"[!] Error updating lead status in CSV: {e}")

def clean_email(email_str: str) -> str:
    cleaned = email_str.lower().strip().rstrip('.,;:()[]{}<>"\'')
    if '@gmail.com' in cleaned:
        idx = cleaned.find('@gmail.com')
        return cleaned[:idx + 10]
    m = re.search(r'([a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z]{2,6}))', cleaned)
    if m:
        return m.group(1)
    return ""

def is_valid_email(email: str, title: str = "", body: str = "") -> bool:
    if not email or '@' not in email:
        return False
    email_clean = email.strip().lower()
    if email_clean in DEAD_EMAIL_BLACKLIST:
        return False

    user, domain = email_clean.split('@', 1)
    if len(user) < 3 or user.isdigit():
        return False

    # Ban generic prefixes like production@, info@, contact@, booking@
    if user in EXCLUDED_USERS:
        return False

    # If domain is gmail.com, block irrelevant vendor usernames (makeup, food, florist, etc.)
    if domain == 'gmail.com':
        if any(bad in user for bad in ['makeup', 'mua', 'food', 'cake', 'mehndi', 'henna', 'florist', 'floral']):
            return False

    if domain in EXCLUDED_DOMAINS:
        return False

    tld = domain.split('.')[-1]
    if tld not in VALID_TLDS:
        return False

    # Rejection of irrelevant vendor types in title/body (e.g. makeup artist or caterer tagged in caption)
    combined_text = f"{title} {body} {user}".lower()
    if any(bad in combined_text for bad in REJECT_VENDORS):
        if not any(req in combined_text for req in REQUIRED_ROLES):
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
        if len(cand) >= 3 and len(cand) <= 35 and cand.lower() not in {'youtube', 'instagram', 'facebook', 'wedding'}:
            return cand.title()

    cleaned = raw_title.split('|')[0].split('•')[0].split('-')[0].split(':')[0].strip()
    cleaned = re.sub(r'(@|Instagram|on Instagram|YouTube|Twitter|X|Facebook|TikTok|Wedding Planner|Event Management|Wedding)', '', cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r'[\(\)\[\]\{\}\<\>•\-:|]', ' ', cleaned).strip()
    words = [w for w in cleaned.split() if len(w) > 1 and not w.isdigit()]
    candidate = " ".join(words[:3])

    invalid = {
        'there', 'team', 'contact', 'admin', 'help', 'jobs', 'official',
        'wedding', 'wedding planner', 'weddings', 'planners', 'events',
        'event management', 'india', 'delhi', 'mumbai', 'jaipur', 'dubai', 'london'
    }
    rejected_prefixes = ['a ', 'an ', 'our ', 'the ', 'best ', 'top ', 'luxury ']
    if len(candidate) >= 3 and len(candidate) <= 35 and candidate.lower() not in invalid and not any(candidate.lower().startswith(p) for p in rejected_prefixes):
        return candidate.title()

    user = email.split('@')[0].lower()
    for prefix in ['reach', 'team', 'contact', 'info', 'business', 'official', 'the', 'weddings', 'events', 'planner']:
        if user.startswith(prefix) and len(user) > len(prefix) + 2:
            user = user[len(prefix):]
    user = user.replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
    clean_words = [w.capitalize() for w in user.split() if not w.isdigit() and len(w) > 1]
    if clean_words:
        cand_user = " ".join(clean_words[:2])
        if cand_user.lower() not in invalid:
            return cand_user

    return "there"

def send_smtp_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: Path = None) -> bool:
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print("[-] Missing Gmail credentials in .env", flush=True)
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{GMAIL_USER}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if attachment_path and attachment_path.exists():
            file_size_mb = attachment_path.stat().st_size / (1024 * 1024)
            if file_size_mb <= 24.0:
                with open(attachment_path, "rb") as f:
                    part = MIMEBase("video", "mp4")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{attachment_path.name}"')
                msg.attach(part)
                print(f"    [📎] Attached: {attachment_path.name} ({file_size_mb:.1f} MB)", flush=True)
            else:
                print(f"    [!] Attachment exceeds 24 MB ({file_size_mb:.1f} MB), skipping to avoid bounce.", flush=True)

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"[-] SMTP Delivery failed for {to_email}: {e}", flush=True)
        return False

def get_current_batch_default() -> str:
    current_hour = time.localtime().tm_hour
    if 5 <= current_hour < 12:
        return "morning"
    elif 12 <= current_hour < 17:
        return "afternoon"
    else:
        return "night"

def run_agent(batch_name=None, max_leads=DEFAULT_BATCH_MAX, send_emails=False, dry_run=False):
    if not batch_name:
        batch_name = get_current_batch_default()
    outreach_enabled = os.getenv("EMAIL_OUTREACH_ENABLED", "false").lower() in ("true", "1", "yes")
    should_send = (send_emails or outreach_enabled) and not dry_run

    target = BATCH_TARGETS.get(batch_name, BATCH_TARGETS["morning"])
    print("\n" + "=" * 70, flush=True)
    print(f" [*] WEDDING & E-INVITATION AI AGENT: {target['name'].upper()}", flush=True)
    print(f" Target Region: {target['geo']}", flush=True)
    print(f" Mode: {'LIVE DISPATCH (Auto-Sending)' if should_send else 'SAFE GATHERING & TELEGRAM PREVIEW (Dry-Run)'}", flush=True)
    print(f" Target Quota: {max_leads} Leads", flush=True)
    print("=" * 70 + "\n", flush=True)

    active_attachment = SAMPLE_VIDEO_PATH if SAMPLE_VIDEO_PATH.exists() and SAMPLE_VIDEO_PATH.stat().st_size / (1024*1024) <= 24 else None
    if active_attachment:
        print(f"[*] Attached sample video: {active_attachment.name} ({active_attachment.stat().st_size / (1024*1024):.1f} MB)", flush=True)

    sent_history = load_sent_history()
    print(f"[*] Loaded {len(sent_history)} previously contacted wedding addresses.", flush=True)

    # 1. First take from pre-queued leads in CSV
    pre_queued = load_queued_leads_from_csv(batch_name)
    print(f"[*] Found {len(pre_queued)} pre-queued leads ready in CSV for {batch_name} batch.", flush=True)

    discovered_leads = []
    seen_in_run = set()

    for row in pre_queued:
        if len(discovered_leads) >= max_leads:
            break
        em = row.get("email", "").strip().lower()
        if em not in sent_history and em not in seen_in_run and is_valid_email(em, row.get("brand_name", "")):
            brand = row.get("brand_name", "")
            if 'cinema' in row.get("service_pitched", "").lower():
                subj, body = get_wedding_cinema_pitch(brand, SENDER_NAME, active_attachment is not None)
                svc = "Wedding Cinema & Motion E-Invites"
            else:
                subj, body = get_wedding_planner_pitch(brand, SENDER_NAME, active_attachment is not None)
                svc = "Luxury Wedding Video Invitations"
            discovered_leads.append({
                "brand_name": brand,
                "email": em,
                "phone": row.get("phone", ""),
                "batch": batch_name,
                "target_region": row.get("target_region", target["geo"]),
                "service_pitched": svc,
                "subject": row.get("subject") or subj,
                "pitch_body": body,
                "source_link": row.get("source_link", ""),
                "status": "QUEUED"
            })
            seen_in_run.add(em)
            print(f"  ⚡ [PRE-QUEUED LEAD] {brand} <{em}> (Phone: {row.get('phone', 'N/A')})", flush=True)

    # 2. If more leads are needed to meet batch quota, scrape live
    if len(discovered_leads) < max_leads:
        needed = max_leads - len(discovered_leads)
        print(f"[*] Pre-queued has {len(discovered_leads)}/{max_leads}. Scanning live web for {needed} more...", flush=True)
        from ddgs import DDGS
        with DDGS(timeout=20) as ddgs:
            for q in target["queries"]:
                if len(discovered_leads) >= max_leads:
                    break

                print(f"[?] Scanning wedding ecosystem: {q}", flush=True)
                try:
                    results = list(ddgs.text(q, max_results=8))
                    for r in results:
                        if len(discovered_leads) >= max_leads:
                            break

                        title = r.get("title", "")
                        body = r.get("body", "")
                        link = r.get("href", "")
                        corpus = f"{title} {body}"

                        if any(neg in corpus.lower() for neg in NEGATIVE_PHRASES):
                            continue

                        emails = EMAIL_REGEX.findall(corpus)
                        valid_candidates = []
                        for em in emails:
                            cleaned = clean_email(em)
                            if cleaned not in sent_history and cleaned not in seen_in_run and is_valid_email(cleaned, title, body):
                                valid_candidates.append(cleaned)

                        if not valid_candidates:
                            continue

                        lead_email = valid_candidates[0]
                        seen_in_run.add(lead_email)

                        phones = extract_phone_numbers(corpus)
                        primary_phone = phones[0] if phones else ""
                        brand_name = clean_brand_name(title, lead_email)

                        # Determine pitch tone
                        if 'cinema' in corpus.lower() or 'photograph' in corpus.lower():
                            subject, pitch_body = get_wedding_cinema_pitch(brand_name, SENDER_NAME, active_attachment is not None)
                            svc_type = "Wedding Cinema & Motion E-Invites"
                        else:
                            subject, pitch_body = get_wedding_planner_pitch(brand_name, SENDER_NAME, active_attachment is not None)
                            svc_type = "Luxury Wedding Video Invitations"

                        lead_record = {
                            "brand_name": brand_name,
                            "email": lead_email,
                            "phone": primary_phone,
                            "batch": batch_name,
                            "target_region": target["geo"],
                            "service_pitched": svc_type,
                            "subject": subject,
                            "pitch_body": pitch_body,
                            "source_link": link,
                            "status": "QUEUED"
                        }
                        discovered_leads.append(lead_record)
                        save_lead_to_csv(lead_record)

                        print(f"  💍 [QUALIFIED WEDDING LEAD] {brand_name} <{lead_email}>", flush=True)
                        if primary_phone:
                            print(f"     📞 Phone / WA: {primary_phone}", flush=True)
                        print(f"     Title: {title[:70]}...", flush=True)

                except Exception as e:
                    print(f"  [-] Search query warning: {e}", flush=True)

                time.sleep(random.uniform(2.5, 3.5))

    print(f"\n[=] Qualified Wedding Leads: {len(discovered_leads)}/{max_leads}", flush=True)
    if not discovered_leads:
        print("[!] No new unique wedding leads found in this search cycle.", flush=True)
        return

    dispatched_count = 0
    telegram_summary = []
    phone_alerts = []

    for idx, lead in enumerate(discovered_leads, start=1):
        brand = lead["brand_name"]
        email = lead["email"]
        phone = lead["phone"]
        subject = lead["subject"]
        body = lead["pitch_body"]
        svc = lead["service_pitched"]

        print(f"\n--- Lead {idx}/{len(discovered_leads)}: {brand} <{email}> ---", flush=True)
        if phone:
            print(f"Phone: {phone}", flush=True)
        print(f"Subject: {subject}", flush=True)

        status = "QUEUED_SAFE"
        if should_send:
            print(f"[>] Dispatching wedding pitch via Gmail TLS...", flush=True)
            success = send_smtp_email_with_attachment(email, subject, body, active_attachment)
            status = "SENT" if success else "FAILED"
            update_lead_status_in_csv(email, status)
            if success:
                dispatched_count += 1
                sent_history.add(email)
                print(f"[+] Delivered! (Batch Progress: {dispatched_count}/{len(discovered_leads)})", flush=True)
            else:
                print(f"[-] Failed to deliver.", flush=True)

            record = {
                "brand_name": brand,
                "email": email,
                "phone": phone,
                "batch": batch_name,
                "target_region": target["geo"],
                "service_pitched": svc,
                "subject": subject,
                "status": status,
                "source_link": lead["source_link"],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            record_sent_lead(record)

            delay = random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
            print(f"[*] Anti-spam spacing: Waiting {delay:.1f}s before next send...", flush=True)
            time.sleep(delay)
        else:
            print("[*] Safe Mode (Dry Run): Lead queued without sending email.", flush=True)

        telegram_summary.append(
            f"💍 *{brand}* (`{email}`)\n"
            f"📞 *Phone/WA*: `{phone if phone else 'N/A'}`\n"
            f"🔗 [Post Link]({lead['source_link']})\n"
            f"📊 *Status*: `{status}`\n"
        )
        if phone:
            clean_digits = re.sub(r'\D', '', phone)
            if len(clean_digits) == 10:
                clean_digits = f"91{clean_digits}"
            wa_link = f"https://wa.me/{clean_digits}"
            phone_alerts.append(f"📞 *{brand}*: `{phone}`\n   👉 [Tap to Open WhatsApp Chat]({wa_link})")

    if phone_alerts:
        phone_msg = f"🔔 *DIRECT WEDDING LEADS WITH PHONE NUMBERS FOUND!*\n\n"
        phone_msg += "\n\n".join(phone_alerts)
        phone_msg += "\n\n💡 _Tap any link above to message them on WhatsApp with high response rate!_"
        send_telegram(phone_msg)

    report = f"💒 *Wedding E-Invitation Leads — {target['name']}*\n"
    report += f"🌍 *Region*: `{target['geo']}`\n"
    report += f"⚡ *Mode*: `{'DISPATCHED' if should_send else 'SAFE GATHERED (No Mails Sent)'}`\n"
    report += f"📁 *Saved in*: `leads/wedding_leads.csv`\n\n"
    report += "\n".join(telegram_summary)
    report += f"\n💌 Attachment: `{'Attached (wedding_e_invite_sample.mp4)' if active_attachment else 'No file'}`"

    send_telegram(report)
    print("\n" + "=" * 70, flush=True)
    print(f" [✔] Batch complete. Saved to wedding_leads.csv & Telegram updated.", flush=True)
    print("=" * 70 + "\n", flush=True)

if __name__ == '__main__':
    default_batch = get_current_batch_default()
    parser = argparse.ArgumentParser(description="Wedding & E-Invitation AI Outreach Agent")
    parser.add_argument("--batch", choices=["morning", "afternoon", "night"], default=default_batch, help=f"Batch to run (default: {default_batch})")
    parser.add_argument("--max", type=int, default=DEFAULT_BATCH_MAX, help="Max leads to process (default: 15)")
    parser.add_argument("--send", action="store_true", default=False, help="Explicitly dispatch emails via Gmail TLS")
    parser.add_argument("--dry-run", action="store_true", default=False, help="Dry run simulation only (no emails sent)")
    parser.add_argument("--force", action="store_true", default=False)
    args = parser.parse_args()

    outreach_env = os.getenv("EMAIL_OUTREACH_ENABLED", "false").lower() in ("true", "1", "yes")

    if args.dry_run:
        dry_run_flag = True
        send_emails_flag = False
    elif args.send or args.force or outreach_env:
        dry_run_flag = False
        send_emails_flag = True
    else:
        dry_run_flag = True
        send_emails_flag = False

    run_agent(batch_name=args.batch, max_leads=args.max, send_emails=send_emails_flag, dry_run=dry_run_flag)
