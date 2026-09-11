"""Subject-specific glass geometry for partner information sections."""

from html import escape

from partner_art import DRAWINGS


def group(markup: str, x: float, y: float, scale: float = 1) -> str:
    return f'<g transform="translate({x} {y}) scale({scale})">{markup}</g>'


MONITOR = '''<path class="pg-side" d="m10 0 12-7 118 13v85l-12 7-118-13z"/>
<rect class="pg-glass" width="128" height="94" rx="6"/>
<rect class="pg-dark" x="9" y="10" width="110" height="69" rx="3"/>
<path class="pg-side" d="M56 94h16v20H56z"/><path class="pg-glass" d="M38 114h52l13 7H25z"/>
<path class="pg-glint" d="m17 18 25 25m-25-12 15 15"/>'''
TERMINAL = '''<path class="pg-side" d="m0 8 12-8 48 11v105l-12 8-48-12z"/>
<path class="pg-glass" d="m0 8 48 11v105L0 112z"/>
<path class="pg-dark" d="m7 23 34 8v35L7 58z"/>
<path class="pg-blue" d="m13 32 22 5v16l-22-5z"/>
<path class="pg-slot" d="m14 80 20 5"/><path class="pg-glass" d="m0 112 48 12 7 7-57-12z"/>'''
SERVER = '''<path class="pg-side" d="m0 8 18-8 62 14v110l-18 8L0 118z"/>
<path class="pg-glass" d="m0 8 62 14v110L0 118z"/>
<path class="pg-dark" d="m9 26 44 10v17L9 43zm0 31 44 10v17L9 74zm0 31 44 10v17L9 105z"/>
<path class="pg-white-line" d="m17 36 22 5m-22 26 22 5m-22 26 22 5"/>'''
PAPER = '''<path class="pg-side" d="m8 0 82 8v108l-8 8L0 116z"/>
<path class="pg-glass" d="M0 8h62l20 20v96H0z"/>
<path class="pg-white" d="M62 8v20h20z"/>
<path class="pg-fine" d="M14 45h52M14 58h42M14 71h47M14 84h27"/>
<path class="pg-code" d="m15 102 9-8 8 8 8-8"/>'''
COIN = '''<circle class="pg-blue" r="23"/><circle class="pg-ring" r="17"/>
<path class="pg-symbol" d="M-6 12v-25H3a6 6 0 0 1 0 12H-10m0 6H4"/>'''
WALLET = '''<path class="pg-side" d="m0 16 19-14 94 17v70L94 101 0 83z"/>
<path class="pg-glass" d="m0 16 94 17v68L0 83z"/>
<path class="pg-glint" d="m8 24 79 14"/><path class="pg-blue" d="m66 52 38 6v26l-38-7z"/>
<circle class="pg-white" cx="78" cy="65" r="4"/>'''
PHONE = '''<path class="pg-side" d="m8 0 54 10v127l-8 7L0 133z"/>
<rect class="pg-glass" y="6" width="54" height="137" rx="8"/>
<rect class="pg-dark" x="6" y="19" width="42" height="99" rx="3"/>
<path class="pg-glint" d="m12 26 24 27M12 40l13 15"/><circle class="pg-side" cx="27" cy="130" r="4"/>'''
BOX = '''<path class="pg-blue" d="m0 26 51-26 51 26v64l-51 27L0 90z"/>
<path class="pg-glass" d="m0 26 51 26 51-26-51-26z"/>
<path class="pg-glint" d="m3 30 48 25 48-25M51 55v56"/>'''
OPEN_BOX = '''<path class="pg-side" d="m0 32 51-26 51 26-51 28z"/>
<path class="pg-glass" d="m0 32-15-14L36-8 51 6zm51-26 16-14 51 26-16 14z"/>
<path class="pg-white" d="M22 13h10v11l6 7v31H16V31l6-7z"/>
<path class="pg-blue" d="M21 9h12v8H21zM17 36h20v13H17z"/>
<path class="pg-glass" d="m48 7 24-10 16 10v53H48z"/>
<path class="pg-blue" d="m48 7 24 9 16-9-16-10z"/>
<path class="pg-fine" d="M60 26h14m-14 9h14"/>
<path class="pg-blue" d="m0 32 51 26v65L0 97zm51 26 51-26v65l-51 26z"/>
<path class="pg-glint" d="m4 37 47 24 47-24M51 62v56"/>
<path class="pg-glass" d="m0 32 51 26-13 17-53-29zm51 26 51-26 14 14-53 29z"/>'''
STORE = '''<path class="pg-side" d="m84 27 14-8v79l-14 9z"/>
<path class="pg-glass" d="M0 27h84v80H0z"/>
<path class="pg-blue" d="m-8 32 20-32h61l20 32z"/>
<path class="pg-white" d="m24 2-12 28h16l7-28zm26 0 6 28h16L61 2z"/>
<path class="pg-dark" d="M10 49h27v36H10zm41 0h23v58H51z"/>
<path class="pg-glass" d="M15 54h17v26H15zm40 0h15v45H55z"/>'''
GEAR = '''<path class="pg-blue" d="M-10-36h20l3 10 9 5 10-3 10 17-7 8v9l7 8-10 17-10-3-9 5-3 10h-20l-3-10-9-5-10 3-10-17 7-8v-9l-7-8 10-17 10 3 9-5z"/>
<circle class="pg-white" cy="5" r="16"/><circle class="pg-side" cy="5" r="8"/>'''
LOCK = '''<path class="pg-slot" d="M-17 0v-17a17 17 0 0 1 34 0V0"/>
<rect class="pg-blue" x="-29" y="-3" width="58" height="48" rx="8"/>
<circle class="pg-white" cy="17" r="6"/><path class="pg-symbol" d="M0 20v10"/>'''
PERSON = '''<circle class="pg-blue" cx="22" cy="17" r="17"/>
<path class="pg-glass" d="M-6 81V63a28 28 0 0 1 56 0v18z"/>
<path class="pg-glint" d="M2 70v-9a20 20 0 0 1 10-17"/>'''
NETWORK_LINES = '<path class="pg-network-line" d="M80 149v32h188v-32M173 181v-46"/>'


SCENES = {
    "maintenance": group(TERMINAL, 107, 38, 1.25) + group(GEAR, 234, 144, .9),
    "remote": NETWORK_LINES + group(MONITOR, 99, 39, 1.2) + group(TERMINAL, 38, 126, .55) + group(TERMINAL, 269, 124, .55),
    "wallet-market": group(MONITOR, 111, 27, 1.1) + '<path class="pg-blue" d="M140 51h22v19h-22zm29 0h22v19h-22zm29 0h22v19h-22zM140 78h22v19h-22zm29 0h22v19h-22zm29 0h22v19h-22z"/>' + group(WALLET, 45, 112, .9) + group(OPEN_BOX, 224, 124, .65),
    "connection": group(PAPER, 82, 41, 1.15) + group(SERVER, 237, 78, .83) + '<path class="pg-network-line" d="M181 119h34v19h24"/><path class="pg-code" d="m200 90 11 11-11 11"/>',
    "security": group(SERVER, 45, 73, .9) + group(SERVER, 244, 73, .9) + '<path class="pg-network-line" d="M110 142h146"/><path class="pg-glass" d="m180 41 58 23v69c0 34-58 63-58 63s-58-29-58-63V64z"/>' + group(LOCK,180,104,.82),
    "processing": NETWORK_LINES + group(SERVER, 44, 88, .88) + group(SERVER, 144, 30, 1.08) + group(SERVER, 251, 88, .88),
    "reports": group(PAPER, 149, 43, 1.15) + group(PAPER, 107, 57, 1.15) + '<g transform="translate(255 164)"><circle class="pg-blue" r="31"/><path class="pg-symbol" d="m-14 0 9 10L15-11"/></g>',
    "wallet": group(PHONE, 105, 36, 1.14) + group(WALLET, 172, 108, 1.0) + group(COIN, 237, 105, .85),
    "preprocessing": '<path class="pg-network-line" d="M83 89h77m-77 78h77m59-56h44m-44 58h44"/>' + group(TERMINAL, 37, 32, .7) + group(PHONE, 48, 133, .5) + group(SERVER, 141, 59, 1.12) + group(STORE, 257, 91, .66),
    "payment-points": group(TERMINAL, 66, 31, 1.12) + group(PHONE, 230, 61, .96) + group(COIN,180,173,1.08),
    "sales": group(TERMINAL, 66, 31, 1.12) + group(PHONE, 230, 61, .96) + group(OPEN_BOX, 146, 133, .66),
    "catalog": group(PAPER, 91, 37, 1.3) + group(OPEN_BOX, 186, 110, .85) + '<path class="pg-blue" d="M102 64h59v12h-59z"/>',
    "orders": group(PAPER, 185, 33, 1.1) + group(OPEN_BOX, 75, 86, 1.0) + '<path class="pg-glass" d="M66 210h220l-17 16H83z"/>',
    "sync": group(MONITOR, 99, 59, 1.15) + '<path class="pg-signal" d="M73 123c-6-56 43-90 85-87m-19-11 20 11-19 14M290 122c6 56-43 90-85 87m19 11-20-11 19-14"/>',
    "supplier-join": group(PAPER, 83, 35, 1.2) + group(OPEN_BOX, 197, 110, .83),
    "network": NETWORK_LINES + group(STORE, 38, 72, .78) + group(STORE, 246, 72, .78) + group(MONITOR, 132, 113, .76),
    "deployment": group(STORE, 128, 28, 1.1) + group(TERMINAL, 48, 105, .72) + group(TERMINAL, 156, 113, .72) + group(TERMINAL, 263, 105, .72) + '<path class="pg-network-line" d="M112 83H69v17m159-17h60v17"/>',
    "cashdesk": group(MONITOR, 93, 34, .92) + '<path class="pg-glass" d="m73 150 192 0 23 21H49z"/><path class="pg-side" d="M61 171h213v18H61zM78 189h12v29H78zm166 0h12v29h-12z"/>' + group(COIN, 244, 129, .95),
    "participants": '<path class="pg-network-line" d="M70 115V92h205v23M179 92V71"/>' + group(PERSON,157,13,.76) + group(TERMINAL,47,111,.77) + group(SERVER,150,107,.73) + group(OPEN_BOX,242,135,.65),
    "gateway-connection": group(PAPER,48,58,.95) + '<path class="pg-code" d="m161 78-21 29 21 29m39-58 21 29-21 29m-13-67-16 75"/><path class="pg-network-line" d="M129 148h106"/>' + group(PAPER,244,58,.78) + '<path class="pg-code" d="m267 156 11 11 21-24"/>',
    "directions": '<path class="pg-network-line" d="M83 121h51m85 0h46"/>' + group(TERMINAL,41,74,.77) + group(GEAR,177,116,1.05) + group(STORE,262,91,.7),
    "operations": group(PAPER,108,38,1.22) + '<g transform="translate(233 151)"><circle class="pg-glass" r="32"/><circle class="pg-signal" r="24"/><path class="pg-slot" d="m23 24 24 28"/><path class="pg-code" d="m-12 0 8 8 16-17"/></g>',
}

SCENE_TYPES = {
    "agent-maintenance": "maintenance", "agent-remote": "remote", "agent-innovation": "wallet-market",
    "provider-payment-points": "payment-points", "provider-connection": "connection",
    "provider-data-security": "security", "provider-processing": "processing",
    "provider-reporting": "reports", "provider-finger": "wallet", "provider-preprocessing": "preprocessing",
    "provider-office-terminal": "deployment",
    "supplier-sales-channels": "sales", "supplier-catalog": "catalog", "supplier-order-management": "orders",
    "supplier-xml": "gateways", "supplier-sync": "sync", "supplier-connection": "supplier-join",
    "retail-orders": "orders", "retail-management": "network", "retail-deployment": "deployment",
    "representative-cashdesk": "cashdesk", "representative-region": "representatives",
    "representative-directions": "directions", "representative-participants": "participants",
    "gateway-steps": "gateway-connection", "gateway-processing": "processing", "gateway-operations": "operations",
}


def render_partner_scene(scene_id: str, instance: str) -> str:
    kind = SCENE_TYPES[scene_id]
    artwork = SCENES.get(kind) or DRAWINGS[kind]
    uid = 'scene-' + escape(instance, quote=True)
    artwork = artwork.replace('partner-suppliers-interior', uid + '-interior')
    definitions = f'''<defs>
      <linearGradient id="{uid}-glass" x1="0" y1="0" x2="1" y2="1">
        <stop stop-color="#fff" stop-opacity=".96"/><stop offset=".46" stop-color="#e3f3fc" stop-opacity=".7"/>
        <stop offset="1" stop-color="#a3c7dc" stop-opacity=".46"/>
      </linearGradient>
      <linearGradient id="{uid}-blue" x1="0" y1="0" x2="1" y2="1">
        <stop stop-color="#249fd5"/><stop offset="1" stop-color="#006caa"/>
      </linearGradient>
    </defs>'''
    ground = '' if kind in DRAWINGS else '<ellipse class="pg-shadow" cx="180" cy="219" rx="119" ry="10"/>'
    return (
        f'<figure class="partner-scene" data-scene="{escape(scene_id, quote=True)}" aria-hidden="true">'
        f'<svg class="partner-infographic partner-scene__art" viewBox="0 0 360 240" focusable="false" '
        f'style="--pg-glass:url(#{uid}-glass);--pg-blue:url(#{uid}-blue)">{definitions}{ground}{artwork}</svg></figure>'
    )
