"""Geometric navigation pictograms, not product renders or live interfaces."""

from html import escape


DRAWINGS = {
    "agents": '''
      <ellipse class="pg-shadow" cx="178" cy="212" rx="110" ry="10"/>
      <g class="pg-object">
        <path class="pg-side" d="m137 29 24-12 72 23-24 12v139l-24 14-48-24z"/>
        <path class="pg-glass" d="m115 40 22-11 72 23v132l-94-26z"/>
        <path class="pg-dark" d="m128 57 67 19v62l-67-19z"/>
        <path class="pg-blue" d="m137 69 48 14v29l-48-13z"/>
        <path class="pg-glint" d="m142 74 38 11m-38 3 20 6"/>
        <path class="pg-slot" d="m137 135 40 12"/>
        <path class="pg-glass" d="m114 158 95 26 16 17-103 12-34-15z"/>
        <path class="pg-side" d="m88 198 34 15 103-12v9l-103 13-34-15z"/>
        <path class="pg-white" d="m144 141 28 8v31l-6-5-6 2-6-5-10 1z"/>
        <path class="pg-fine" d="m150 151 16 5m-16 3 11 3"/>
      </g>
      <g class="pg-detail">
        <circle class="pg-blue" cx="253" cy="162" r="31"/>
        <circle class="pg-ring" cx="253" cy="162" r="23"/>
        <path class="pg-symbol" d="M246 177v-31h11a8 8 0 0 1 0 16h-17m0 7h17"/>
      </g>''',
    "providers": '''
      <ellipse class="pg-shadow" cx="179" cy="211" rx="113" ry="10"/>
      <g class="pg-object">
        <path class="pg-side" d="m125 160 23-42 15 7-21 43z"/>
        <path class="pg-glass" d="m104 189 38-21 39 14-37 23z"/>
        <path class="pg-side" d="m104 189 40 16 37-23v9l-37 23-40-15z"/>
        <path class="pg-glass" d="M76 70c-5 59 37 102 95 93z"/>
        <path class="pg-blue" d="M76 70c48-11 94 37 95 93-39-2-89-48-95-93z"/>
        <path class="pg-glint" d="M85 75c20 2 56 26 70 59"/>
        <path class="pg-slot" d="m125 120 54-55"/>
        <circle class="pg-dark" cx="181" cy="63" r="9"/>
        <path class="pg-signal" d="M205 40a37 37 0 0 1 1 45m15-59a57 57 0 0 1 0 74"/>
      </g>
      <g class="pg-detail">
        <path class="pg-glass" d="m205 165 63-13 27 17-62 15z"/>
        <path class="pg-side" d="m233 184 62-15v23l-62 15z"/>
        <path class="pg-glass" d="m205 165 28 19v23l-28-19z"/>
        <path class="pg-slot" d="M257 154v-34m20 40v-29"/>
        <path class="pg-white-line" d="m244 190 27-7"/>
      </g>''',
    "suppliers": '''
      <ellipse class="pg-shadow" cx="178" cy="215" rx="111" ry="10"/>
      <g class="pg-object">
        <path class="pg-dark" d="m94 116 83-42 85 42-85 42z"/>
        <path class="pg-glass" d="m94 116 83 42v60l-83-44z"/>
        <path class="pg-side" d="m177 158 85-42v58l-85 44z"/>
        <path class="pg-blue" d="m113 86 37-19 36 18v45l-36 20-37-20z"/>
        <path class="pg-glint" d="m115 88 35 18 33-19m-33 19v38"/>
        <path class="pg-glass" d="M192 59h42v76c0 16-42 16-42 0z"/>
        <ellipse class="pg-white" cx="213" cy="59" rx="21" ry="9"/>
        <path class="pg-glass" d="m94 116-29 24 83 42 29-24z"/>
        <path class="pg-glass" d="m177 158 31 24 85-43-31-23z"/>
        <path class="pg-glint" d="m98 173 69 36m20-1 65-34"/>
      </g>
      <path class="pg-detail pg-glass" d="m95 116-20-21 80-41 22 20zm82-42 23-20 84 42-22 20z"/>''',
    "retail": '''
      <ellipse class="pg-shadow" cx="177" cy="214" rx="129" ry="10"/>
      <g class="pg-back">
        <path class="pg-glass" d="M40 87h75v76H40zM244 87h75v76h-75z"/>
        <path class="pg-side" d="m115 87 13-9v77l-13 8m204-76 12-9v77l-12 8"/>
        <path class="pg-blue" d="m33 91 15-29h60l14 29zm204 0 15-29h60l14 29z"/>
        <path class="pg-white" d="m54 63-8 27h16l4-27zm30 0 3 27h16l-8-27zm174 0-8 27h16l4-27zm30 0 3 27h16l-8-27z"/>
        <path class="pg-window" d="M52 110h21v32H52zm29 0h20v53H81zm175 0h21v32h-21zm29 0h20v53h-20z"/>
      </g>
      <g class="pg-object">
        <path class="pg-side" d="m223 111 22-13v99l-22 14z"/>
        <path class="pg-glass" d="M114 111h109v100H114z"/>
        <path class="pg-blue" d="m102 116 23-43h88l25 43z"/>
        <path class="pg-white" d="m135 75-14 39h22l7-39zm35 0 3 39h22l-10-39z"/>
        <path class="pg-dark" d="M126 136h41v52h-41zm55 0h29v75h-29z"/>
        <path class="pg-glass" d="M130 140h33v43h-33zm55 0h21v56h-21z"/>
        <path class="pg-glint" d="m134 145 23 22m-23-8 15 15m42-29 10 10"/>
        <path class="pg-dark" d="M107 211h124v8H107z"/>
      </g>''',
    "representatives": '''
      <ellipse class="pg-shadow" cx="180" cy="213" rx="118" ry="10"/>
      <g>
        <path class="pg-glass" d="m65 147 70-29v73l-70 30z"/>
        <path class="pg-side" d="m135 118 82 26v73l-82-26z"/>
        <path class="pg-glass" d="m217 144 75-30v73l-75 30z"/>
        <path class="pg-map-line" d="m79 166 42-18 62 34 77-36m-178 56 42-17 56 19 92-40"/>
        <circle class="pg-blue" cx="94" cy="194" r="6"/>
        <circle class="pg-blue" cx="263" cy="145" r="6"/>
      </g>
      <g class="pg-object">
        <path class="pg-side" d="m181 168 16-5 39-64-18 5z"/>
        <path class="pg-blue" d="m137 93 44 76 44-76z"/>
        <circle class="pg-side" cx="193" cy="77" r="46"/>
        <circle class="pg-blue" cx="181" cy="81" r="46"/>
        <circle class="pg-white" cx="181" cy="81" r="20"/>
        <circle class="pg-glass" cx="184" cy="79" r="13"/>
        <path class="pg-glint" d="M145 77a37 37 0 0 1 44-31"/>
      </g>''',
    "gateways": '''
      <ellipse class="pg-shadow" cx="178" cy="214" rx="121" ry="10"/>
      <g class="pg-object">
        <path class="pg-side" d="m54 58 18-11 83 25-17 11v116l-17 10-67-22z"/>
        <path class="pg-glass" d="m54 58 84 25v116l-84-26z"/>
        <path class="pg-code" d="m82 107-13 9 13 16m30-17 13 16-13 8m-11-34-11 40"/>
        <path class="pg-side" d="m224 61 20-10 64 20v116l-20 11-64-20z"/>
        <path class="pg-glass" d="m205 73 83 25v100l-83-25z"/>
        <path class="pg-dark" d="m218 96 57 17v16l-57-17zm0 29 57 17v16l-57-17zm0 29 57 17v16l-57-17z"/>
        <path class="pg-white-line" d="m227 107 24 7m-24 22 24 7m-24 22 24 7"/>
      </g>
      <g class="pg-detail">
        <path class="pg-blue" d="M127 75h65V60l30 27-30 27V99h-65z"/>
        <path class="pg-glass" d="M230 173h-65v15l-30-27 30-27v15h65z"/>
        <path class="pg-glint" d="M135 80h63m-50 79h73"/>
      </g>''',
}


def render_partner_art(kind: str) -> str:
    if kind not in DRAWINGS:
        raise ValueError(f"Unknown partner illustration: {kind}")
    key = escape(kind, quote=True)
    prefix = f"partner-{key}"
    definitions = f'''
      <defs>
        <linearGradient id="{prefix}-glass" x1="0" y1="0" x2="1" y2="1">
          <stop stop-color="#fff" stop-opacity=".93"/>
          <stop offset=".46" stop-color="#e3f3fc" stop-opacity=".62"/>
          <stop offset="1" stop-color="#a3c7dc" stop-opacity=".38"/>
        </linearGradient>
        <linearGradient id="{prefix}-blue" x1="0" y1="0" x2="1" y2="1">
          <stop stop-color="#249fd5"/>
          <stop offset="1" stop-color="#006caa"/>
        </linearGradient>
      </defs>'''
    return (
        f'<span class="partner-tile__graphic partner-tile__graphic--{key}" aria-hidden="true">'
        f'<svg class="partner-infographic partner-infographic--{key}" '
        f'viewBox="0 0 360 240" focusable="false" '
        f'style="--pg-glass:url(#{prefix}-glass);--pg-blue:url(#{prefix}-blue)">'
        f'{definitions}{DRAWINGS[kind]}</svg></span>'
    )
