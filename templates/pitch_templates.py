"""
=============================================================================
WEDDING & E-INVITATION PITCH TEMPLATES
=============================================================================
High-converting B2B outreach copy tailored for:
1. Luxury Wedding Planners & Event Management Agencies
2. Wedding Cinematographers & Photographers
3. Destination Wedding Coordinators & Invitation Studios
=============================================================================
"""

def get_wedding_planner_pitch(brand_name: str, sender_name: str, has_attachment: bool = True) -> tuple[str, str]:
    greeting = f"Hey {brand_name}," if brand_name.lower() != "there" else "Hey there,"
    subject = f"Royal 3D Video Invitations for your wedding couples, {brand_name}" if brand_name.lower() != "there" else "Royal 3D Video Invitations for your upcoming wedding couples"

    attachment_line = (
        "I've attached 1 quick demo video invite we crafted [see attached video] so you can review our visual pacing and 3D floral aesthetic."
        if has_attachment else
        "I'd love to share a quick 60s demo reel showing our recent caricature and 3D floral wedding invitation designs."
    )

    body = f"""{greeting}

Checked out the stunning wedding experiences and events you manage at {brand_name}—truly elegant aesthetic!

Traditional paper wedding cards are quickly fading out. Modern brides and grooms now specifically request cinematic 60–90s vertical video invitations (with custom animated caricatures, their personal love story sequence, venue Google Maps integration, and WhatsApp/Instagram RSVP buttons).

We partner with premium wedding planners and event management studios to deliver broadcast-quality 3D & motion video invitations within 24–48 hours, 100% white-labeled under your brand name.

{attachment_line}

I'd love to design 1 free custom sample concept for your upcoming wedding couple completely on the house, so you can test our turnaround speed and quality with zero obligations.

Would you be open to checking out a quick custom concept for one of your couples?

Best regards,
{sender_name} | Creative Lead"""

    return subject, body

def get_wedding_cinema_pitch(brand_name: str, sender_name: str, has_attachment: bool = True) -> tuple[str, str]:
    greeting = f"Hey {brand_name}," if brand_name.lower() != "there" else "Hey there,"
    subject = f"Motion E-Invites & Teaser Edits for {brand_name}" if brand_name.lower() != "there" else "Motion E-Invites & Wedding Teaser Edits"

    body = f"""{greeting}

Love the cinematic storytelling and colors in your recent wedding films at {brand_name}!

Couples booking premium wedding cinematography almost always ask for vertical Save-The-Date motion graphics and animated video invites to announce their wedding on Instagram and WhatsApp prior to the main ceremonies.

We partner with wedding photography studios to deliver custom 3D motion invites and fast-turnaround teaser cuts within 24–48 hours under your studio's branding.

I'd love to produce 1 free sample video invite for your next booking so you can offer it as an exclusive add-on package to your clients.

Mind if I send over our latest sample invite reel?

Best regards,
{sender_name} | Creative Lead"""

    return subject, body
