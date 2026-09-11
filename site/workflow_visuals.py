"""Responsive functional diagrams; all explanatory labels come from source data."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json

ROOT = Path(__file__).resolve().parents[1]
SCENES = json.loads((ROOT/'data/workflow-visuals.json').read_text(encoding='utf-8'))['scenes']
TERMINAL = 'assets/originals/FastPay Simple.png'
FINGER = 'assets/originals/logotip_finger.png'
MARKET = 'assets/originals/logotip_skymarket_3x1.png'
ASSET_SIZES = {a['path']: (a.get('width'), a.get('height')) for a in
               json.loads((ROOT/'data/assets-manifest.json').read_text(encoding='utf-8'))['assets'] if a.get('path')}


def img(path, alt='', css='flow-image'):
    width, height = ASSET_SIZES.get(path, (None, None))
    dimensions = f' width="{width}" height="{height}"' if width and height else ''
    return f'<img class="{css}" src="/{quote(path, safe="/")}" alt="{escape(alt)}"{dimensions} loading="lazy" decoding="async">'


def market():
    return img(MARKET, 'SkyMarket', 'flow-market')


def fork(*, inward=False):
    path=('M150 0v20h300V0M300 20v26m-6-6 6 6 6-6' if inward else
          'M300 0v20M150 20h300M150 20v26m-6-6 6 6 6-6M450 20v26m-6-6 6 6 6-6')
    return f'<svg class="flow-fork" viewBox="0 0 600 52" aria-hidden="true" focusable="false"><path d="{path}"/></svg>'


def channels(labels, *, compact=False):
    assets=(TERMINAL,FINGER)
    css='flow-channels flow-channels--compact' if compact else 'flow-channels'
    return f'<div class="{css}">' + ''.join(
        f'<div class="flow-channel">{img(asset, "", "flow-channel__image")}<strong>{escape(label)}</strong></div>'
        for label,asset in zip(labels,assets)) + '</div>'


def management(s):
    controls=''.join(f'<li>{escape(x)}<span aria-hidden="true">→</span></li>' for x in s['controls'])
    observe=''.join(f'<li>{escape(x)}</li>' for x in s['observe'])
    devices = (f'<div class="flow-device-network">{img(TERMINAL)}{img(TERMINAL)}</div>'
               if s.get('network') else img(TERMINAL))
    return (f'<div class="flow-heading">{escape(s["title"])}</div>'
            '<div class="flow-management">'
            f'<div class="flow-management__labels"><div class="flow-group"><span class="flow-kicker">Настройка</span><ul>{controls}</ul></div>'
            f'<div class="flow-group flow-group--observe"><span class="flow-kicker">Контроль</span><ul>{observe}</ul></div></div>'
            f'<div class="flow-management__device">{devices}<strong>{escape(s["target"])}</strong></div></div>')


def payment_channels(s):
    return (f'<div class="flow-service"><strong>{escape(s["title"])}</strong><span>{" · ".join(map(escape,s["fields"]))}</span></div>'
            + fork() + channels(s['channels']))


def processing(s):
    servers=''.join(f'<div class="flow-datacentre">{img("assets/icons/process/server.svg", "", "flow-server")}<strong>{escape(x)}</strong></div>' for x in s['locations'])
    return (f'<div class="flow-heading">{escape(s["title"])}</div><p class="flow-subtitle">{escape(s["distribution"])}</p>'
            + fork() + f'<div class="flow-datacentres">{servers}</div>'
            f'<div class="flow-tunnel"><span aria-hidden="true">↔</span><strong>{escape(s["link"])}</strong><span aria-hidden="true">↔</span></div>'
            f'<p class="flow-sync-label">{escape(s["sync"])}</p>')


def sales(s):
    steps=''.join(f'<li>{escape(x)}</li>' for x in s['steps'])
    return (f'<p class="flow-subtitle">{escape(s["title"])}</p>' + channels(s['channels'],compact=True)
            + fork(inward=True) + f'<div class="flow-shared">{market()}<ol class="flow-steps">{steps}</ol></div>')


def exchange(s):
    lanes=''.join(f'<div class="flow-lane flow-lane--{escape(x["direction"])}"><span>{escape(x["label"])}</span><i aria-hidden="true"></i></div>' for x in s['lanes'])
    return (f'<div class="flow-protocol">{escape(s["title"])}</div>'
            f'<div class="flow-endpoints"><strong>{escape(s["origin"])}</strong>{market()}</div>'
            f'<div class="flow-lanes">{lanes}</div>')


def catalogue_sync(s):
    return (f'<p class="flow-subtitle">{escape(s["title"])}</p>'
            f'<div class="flow-origins"><strong>{escape(s["origins"][0])}</strong><span>или</span><strong>{escape(s["origins"][1])}</strong></div>'
            + fork(inward=True) + f'<div class="flow-shared">{market()}<p>{escape(s["changes"])}</p></div>'
            + fork() + channels(s['channels'],compact=True))


def alternatives(s):
    rows=''.join(f'<div class="flow-option"><strong>{escape(x["action"])}</strong><span>{escape(x["label"])}</span></div>' for x in s['choices'])
    return f'<div class="flow-heading">{escape(s["title"])}</div><div class="flow-options">{rows}</div>'


def operator(s):
    return (f'<div class="flow-heading">{escape(s["title"])}</div>'
            f'<div class="flow-rma-screen">{img("assets/originals/RMA_win_lin.png", s["caption"])}</div>'
            f'<div class="flow-platforms">{"".join(f"<span>{escape(x)}</span>" for x in s["platforms"])}</div>'
            f'<p class="flow-footnote">{escape(s["secondary"])}</p>')


RENDERERS={'management':management,'payment-channels':payment_channels,'processing':processing,
           'sales':sales,'exchange':exchange,'catalogue-sync':catalogue_sync,'alternatives':alternatives,'operator':operator}


def render_workflow_visual(scene_id):
    lookup='provider-processing' if scene_id=='gateway-processing' else scene_id
    if lookup not in SCENES:
        return None
    s=SCENES[lookup]
    return (f'<figure class="workflow-visual workflow-visual--{s["type"]}" data-scene="{escape(scene_id)}" '
            f'aria-label="{escape(s["title"])}">{RENDERERS[s["type"]](s)}</figure>')
