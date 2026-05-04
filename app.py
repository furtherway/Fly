#!/usr/bin/env python3
"""
Trademark Insights MÃƒÂ©xico Ã¢â‚¬â€ TIM
Flask server: ORCH_ONE + Redes Sociales + Dominios + MUA
Corre: python app.py  Ã¢â€ â€™  http://localhost:5050
"""
import json, os, queue, subprocess, sys, threading
from datetime import datetime
from pathlib import Path
from flask import Flask, Response, send_file, request, render_template_string

# Ã¢â€â‚¬Ã¢â€â‚¬ Playwright: asegura que el browser estÃƒÂ© instalado al arrancar Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_PW_PATH = os.path.join(_PROJECT_DIR, ".playwright")
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", _PW_PATH)

def _ensure_playwright_browser():
    """Instala Chromium si no estÃƒÂ¡ disponible. Se ejecuta una sola vez al arrancar."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Si esto funciona, el browser ya estÃƒÂ¡ instalado
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            browser.close()
        print("[startup] Playwright Chromium OK")
    except Exception:
        print("[startup] Playwright Chromium no encontrado Ã¢â‚¬â€ instalandoÃ¢â‚¬Â¦")
        try:
            env = {**os.environ, "PLAYWRIGHT_BROWSERS_PATH": _PW_PATH}
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                check=True, env=env, timeout=300
            )
            print("[startup] Playwright Chromium instalado correctamente")
        except Exception as e:
            print(f"[startup] ERROR instalando Playwright: {e}")

_ensure_playwright_browser()

app = Flask(__name__)

class StreamCapture:
    def __init__(self, q, original):
        self.q = q; self.original = original
    def write(self, text):
        self.original.write(text)
        if text.strip(): self.q.put(("log", text.rstrip()))
    def flush(self): self.original.flush()

def parse_classes(mode, raw):
    import re
    if mode == "T": return list(range(1, 46))
    if mode == "S": return list(range(35, 46))
    if mode == "P": return list(range(1, 35))
    tokens = [t.strip() for t in raw.split(",") if t.strip()]
    classes = set()
    for t in tokens:
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", t)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a > b: a, b = b, a
            for x in range(a, b + 1):
                if 1 <= x <= 45: classes.add(x)
        elif re.fullmatch(r"\d+", t):
            x = int(t)
            if 1 <= x <= 45: classes.add(x)
    return sorted(classes)

HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>TIM Ã¢â‚¬â€ Trademark Insights MÃƒÂ©xico</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;600&family=Lora:ital,wght@0,400;0,600;0,700;1,400;1,600;1,700&family=Raleway:wght@300;400;500;600;700&family=Outfit:wght@300;400;700;900&family=EB+Garamond:ital,wght@0,400;0,700;1,400;1,600&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script>
  const _SB_URL = 'https://clocqafpuquorpydptcu.supabase.co';
  const _SB_KEY = 'sb_publishable_esYY5oS5X60kLaPQZhHLdw_jVWkObUl';
  const sbClient = window.supabase ? window.supabase.createClient(_SB_URL, _SB_KEY) : null;
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
/* Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
   DESIGN TOKENS Ã¢â‚¬â€ Executive Dark / Red accent
Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --white:#ffffff;
  --bg:#ffffff;
  --surface:#f5f5f5;
  --surface2:#ebebeb;
  --navy:#1a1a1a;
  --navy2:#333333;
  --blue:#1540F0;
  --blue-hover:#0f34cc;
  --blue-light:rgba(21,64,240,.12);
  --blue-mid:rgba(21,64,240,.35);
  --sky:rgba(21,64,240,.08);
  --border:#e0e0e0;
  --border2:#d0d0d0;
  --text:#1a1a1a;
  --text2:#555555;
  --muted:#666666;
  --muted2:#999999;
  --green:#22c55e;
  --green-bg:rgba(34,197,94,.1);
  --green-border:rgba(34,197,94,.3);
  --red:#1540F0;
  --red-bg:rgba(21,64,240,.12);
  --red-border:rgba(21,64,240,.35);
  --orange:#f59e0b;
  --shadow-sm:0 1px 3px rgba(0,0,0,.08);
  --shadow:0 2px 8px rgba(0,0,0,.12);
  --shadow-md:0 4px 20px rgba(0,0,0,.15);
  --radius:8px;
  --radius-sm:4px;
  --mono:'IBM Plex Mono',monospace;
  --sans:'Inter','Arial',system-ui,sans-serif;
  --lora:'Lora','Georgia',serif;
}
html,body{min-height:100vh;background:var(--bg);color:var(--text);font-family:var(--sans);font-size:14px;line-height:1.5}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Layout Ã¢â€â‚¬Ã¢â€â‚¬ */
.app-shell{display:flex;flex-direction:column;min-height:100vh}
.topbar{background:#1540F0;border-bottom:3px solid rgba(255,255,255,.15);padding:0 28px;display:flex;align-items:center;gap:12px;height:64px;position:sticky;top:0;z-index:100;box-shadow:0 4px 24px rgba(21,64,240,.45)}
.topbar-logo{display:flex;align-items:center;text-decoration:none;position:absolute;left:50%;transform:translateX(-50%);white-space:nowrap}
.wordmark{font-family:Georgia,'Times New Roman',serif;font-size:32px;font-weight:400;font-style:italic;color:#ffffff;letter-spacing:-0.01em;line-height:1}
.logo-divider{width:1px;height:36px;background:rgba(255,255,255,.35);flex-shrink:0;margin:0 14px;align-self:center}
.by-block{display:flex;flex-direction:column;align-items:flex-start;gap:2px;line-height:1.15}
.by-label{font-family:Georgia,'Times New Roman',serif;font-size:9px;color:rgba(255,255,255,.5);letter-spacing:2px;text-transform:uppercase;margin-bottom:4px}
.tm-trademark{font-family:Georgia,'Times New Roman',serif;font-size:11px;font-weight:400;color:#ffffff}
.tm-insights{font-family:Georgia,'Times New Roman',serif;font-size:11px;font-weight:700;font-style:italic;color:#ffffff}
.tm-mexico{font-family:Georgia,'Times New Roman',serif;font-size:11px;font-weight:400;color:#ffffff}

.topbar-spacer{flex:1}
.btn-nuevo{background:#ffffff;border:1px solid #ffffff;color:#1540F0;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:7px 16px;border-radius:var(--radius-sm);cursor:pointer;transition:all .2s;box-shadow:0 2px 10px rgba(0,0,0,.18)}
.btn-nuevo:hover{background:rgba(255,255,255,.88);border-color:rgba(255,255,255,.88);box-shadow:0 4px 18px rgba(0,0,0,.28)}
.main{max-width:1200px;margin:0 auto;padding:32px 24px 80px;width:100%}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Cards Ã¢â€â‚¬Ã¢â€â‚¬ */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:16px;box-shadow:var(--shadow-sm)}
.card-title{font-size:10px;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--muted);margin-bottom:16px}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Wizard step bar Ã¢â€â‚¬Ã¢â€â‚¬ */
.wiz-bar{display:flex;align-items:center;margin-bottom:32px;position:relative;padding:0 16px}
.wiz-bar::before{content:'';position:absolute;top:16px;left:calc(16px + 44px);right:calc(16px + 44px);height:1px;background:var(--border2);z-index:0}
.wiz-fill{position:absolute;top:16px;left:calc(16px + 44px);height:1px;background:var(--blue);z-index:1;transition:width .5s cubic-bezier(.4,0,.2,1);width:0}
.wiz-node{display:flex;flex-direction:column;align-items:center;gap:6px;flex:1;position:relative;z-index:2}
.wiz-circle{width:32px;height:32px;border-radius:50%;border:1px solid var(--border2);background:var(--surface2);display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:12px;font-weight:700;color:var(--muted);transition:all .3s;box-shadow:var(--shadow-sm)}
.wiz-circle.active{border-color:var(--blue);background:var(--blue);color:#fff;box-shadow:0 0 0 4px rgba(21,64,240,.15)}
.wiz-circle.done{border-color:var(--green);background:var(--green);color:#fff}
.wiz-label{font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--muted);white-space:nowrap;transition:color .3s}
.wiz-label.active{color:var(--blue)}
.wiz-label.done{color:var(--green)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Wizard steps Ã¢â€â‚¬Ã¢â€â‚¬ */
.wiz-step{display:none}
.wiz-step.active{display:block;animation:fadeUp .3s ease}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
.btn-back{display:inline-flex;align-items:center;gap:6px;background:none;border:1px solid var(--border2);color:var(--muted);font-family:var(--mono);font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;padding:7px 14px;border-radius:var(--radius-sm);cursor:pointer;margin-bottom:20px;transition:all .2s}
.btn-back:hover{border-color:var(--blue);color:var(--blue)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Giro selector Ã¢â€â‚¬Ã¢â€â‚¬ */
.giro-search-wrap{position:relative;margin-bottom:14px}
.giro-search{width:100%;padding:12px 16px 12px 40px;background:var(--surface2);border:1px solid var(--border2);border-radius:var(--radius-sm);font-size:14px;color:var(--text);outline:none;transition:border-color .2s;font-family:var(--sans)}
.giro-search:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(21,64,240,.12)}
.giro-search::placeholder{color:var(--muted2)}
.giro-search-icon{position:absolute;left:13px;top:50%;transform:translateY(-50%);color:var(--muted);font-size:15px;pointer-events:none}
.giro-grid{display:flex;flex-direction:column;gap:5px;max-height:420px;overflow-y:auto;padding-right:4px;overflow-x:hidden}
.giro-grid::-webkit-scrollbar{width:4px}
.giro-grid::-webkit-scrollbar-track{background:transparent}
.giro-grid::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}
.giro-card{display:flex;align-items:flex-start;gap:10px;padding:12px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);cursor:pointer;transition:all .2s;position:relative}
.giro-card:hover{border-color:var(--border2);background:var(--surface)}
.giro-card.selected{border-color:var(--blue);background:rgba(21,64,240,.08)}
.giro-card.selected::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--blue);border-radius:var(--radius-sm) 0 0 var(--radius-sm)}
.giro-cls-badge{flex-shrink:0;width:32px;height:32px;border-radius:6px;background:var(--border2);display:flex;align-items:center;justify-content:center;font-family:var(--mono);font-size:11px;font-weight:700;color:var(--muted);margin-top:1px}
.giro-card.selected .giro-cls-badge{background:var(--blue);color:#fff}
.giro-info{flex:1;min-width:0}
.giro-cat{font-size:12px;font-weight:600;color:var(--text);line-height:1.3;margin-bottom:2px}
.giro-desc{font-size:10px;color:var(--muted);line-height:1.4;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.giro-type-pill{display:inline-block;font-size:9px;font-weight:600;letter-spacing:1px;text-transform:uppercase;padding:2px 7px;border-radius:20px;margin-bottom:4px}
.giro-type-pill.prod{background:rgba(29,106,245,.12);color:#60a5fa}
.giro-type-pill.serv{background:rgba(34,197,94,.1);color:#4ade80}
.giro-selected-banner{display:none;align-items:center;gap:12px;padding:12px 16px;background:rgba(21,64,240,.1);border:1px solid rgba(21,64,240,.3);border-radius:var(--radius-sm);margin-bottom:14px}
.giro-selected-banner.show{display:flex}
.gsb-cls{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--blue);flex-shrink:0}
.gsb-info{flex:1}
.gsb-cat{font-size:13px;font-weight:600;color:var(--text)}
.gsb-note{font-size:11px;color:var(--muted);margin-top:2px}
.gsb-clear{background:none;border:none;color:var(--muted);font-size:14px;cursor:pointer;padding:4px;transition:color .2s}
.gsb-clear:hover{color:var(--blue)}
/* Giro accordion */
.giro-row{border:1px solid var(--border);border-radius:var(--radius-sm);overflow:hidden;background:var(--surface2);transition:border-color .15s;flex-shrink:0}
.giro-row:hover{border-color:var(--border2)}
.giro-row.cls-selected{border-color:var(--blue)!important}
.giro-row-head{display:flex;align-items:center;gap:8px;padding:12px 14px;min-height:44px;cursor:pointer;user-select:none;transition:background .15s}
.giro-row-head:hover{background:rgba(255,255,255,.04)}
.giro-row.open>.giro-row-head{background:rgba(255,255,255,.03)}
.giro-row.cls-selected>.giro-row-head{background:rgba(21,64,240,.1)}
.giro-num-badge{font-family:var(--mono);font-size:12px;font-weight:700;color:var(--blue);flex-shrink:0;width:24px;text-align:center}
.giro-heading-text{flex:1;font-size:13px;font-weight:600;color:var(--text);line-height:1.3}
.giro-item-count{font-size:10px;color:var(--muted2);flex-shrink:0;font-family:var(--mono);padding:2px 6px;background:var(--surface);border-radius:99px;border:1px solid var(--border)}
.giro-chevron{font-size:9px;color:var(--muted);transition:transform .2s;flex-shrink:0;margin-left:2px}
.giro-row.open .giro-chevron{transform:rotate(180deg)}
.giro-items-wrap{display:none;padding:4px 12px 10px 38px;gap:5px;flex-wrap:wrap}
.giro-row.open .giro-items-wrap{display:flex}
.giro-chip{font-size:11px;padding:4px 10px;border-radius:99px;border:1px solid var(--border2);color:var(--muted);cursor:pointer;transition:all .15s;background:transparent;line-height:1.4}
.giro-chip:hover{border-color:var(--blue);color:var(--text);background:rgba(21,64,240,.07)}
.giro-chip.selected{background:var(--blue);border-color:var(--blue);color:#fff}
.giro-chip mark,.giro-heading-text mark{background:rgba(255,220,0,.22);color:inherit;border-radius:2px;padding:0 1px}
.giro-hint{padding:20px;text-align:center;color:var(--muted2);font-size:12px;line-height:1.6}
.giro-filter-pills{display:flex;gap:6px;margin-bottom:10px}
.gfp{font-size:10px;font-weight:600;letter-spacing:1px;text-transform:uppercase;padding:5px 12px;border-radius:20px;border:1px solid var(--border2);background:transparent;color:var(--muted);cursor:pointer;transition:all .2s}
.gfp:hover{border-color:var(--border2);color:var(--text)}
.gfp.active{background:var(--blue);border-color:var(--blue);color:#fff}
.giro-empty{padding:32px;text-align:center;color:var(--muted);font-size:12px;letter-spacing:1px;text-transform:uppercase}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Step 1 hero Ã¢â€â‚¬Ã¢â€â‚¬ */
.hero-grid{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}
@media(max-width:768px){.hero-grid{grid-template-columns:1fr}}
.hero-tagline{padding-top:8px}
.tagline-eyebrow{font-size:10px;letter-spacing:4px;text-transform:uppercase;color:var(--muted);font-weight:600;margin-bottom:12px}
.tagline-h1{font-family:var(--lora);font-size:clamp(28px,3vw,44px);font-weight:700;color:var(--text);line-height:1.2;margin-bottom:16px;letter-spacing:-.5px}
.tagline-h1 em{color:var(--blue);font-style:italic}
.tagline-body{font-size:13px;color:var(--muted);line-height:1.7;max-width:340px}
.tagline-checklist{list-style:none;margin-top:18px;display:flex;flex-direction:column;gap:8px}
.tagline-checklist li{display:flex;align-items:flex-start;gap:10px;font-size:12px;color:var(--text2)}
.tagline-checklist li::before{content:'Ã¢â€ â€™';color:var(--blue);font-family:var(--mono);font-weight:700;flex-shrink:0;margin-top:1px}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Analysis type selector Ã¢â€â‚¬Ã¢â€â‚¬ */
.analysis-types{display:grid;grid-template-columns:repeat(auto-fill,minmax(185px,1fr));gap:10px;margin-bottom:20px}
.at-card{display:flex;align-items:center;gap:12px;padding:14px 16px;border:1px solid var(--border2);border-radius:var(--radius-sm);cursor:pointer;transition:all .2s;user-select:none;background:var(--surface2)}
.at-card:hover{border-color:rgba(21,64,240,.4);background:rgba(21,64,240,.06)}
.at-card.selected{border-color:var(--blue);background:rgba(21,64,240,.1)}
.at-card.selected::before{display:none}
.at-icon{width:36px;height:36px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;background:var(--surface);border:1px solid var(--border2)}
.at-card.selected .at-icon{background:var(--blue-light);border-color:rgba(21,64,240,.4)}
.at-info{flex:1;min-width:0}
.at-name{font-size:13px;font-weight:600;color:var(--text);margin-bottom:2px}
.at-desc{font-size:10px;color:var(--muted)}
.at-check{width:18px;height:18px;border-radius:50%;border:1px solid var(--border2);flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:all .2s;background:transparent}
.at-card.selected .at-check{background:var(--blue);border-color:var(--blue)}
.at-card.selected .at-check::after{content:'Ã¢Å“â€œ';color:#fff;font-size:10px;font-weight:700}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Brand inputs Ã¢â€â‚¬Ã¢â€â‚¬ */
.brand-list{display:flex;flex-direction:column;gap:10px;margin-bottom:14px}
.brand-row{display:flex;align-items:center;gap:8px}
.brand-num{width:24px;height:24px;border-radius:50%;background:rgba(21,64,240,.15);border:1px solid rgba(21,64,240,.4);color:var(--blue);font-family:var(--mono);font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.brand-row input{flex:1;padding:12px 14px;border:1px solid var(--border2);border-radius:var(--radius-sm);font-family:Arial,'Helvetica Neue',sans-serif;font-size:18px;font-weight:600;color:var(--text);background:var(--surface2);outline:none;transition:border-color .2s,box-shadow .2s;letter-spacing:.5px}
.brand-row input:focus{border-color:var(--blue);box-shadow:0 0 0 3px rgba(21,64,240,.1)}
.brand-row input::placeholder{color:var(--muted2);font-size:14px;font-weight:400;font-family:var(--sans);letter-spacing:0}
.btn-star{width:32px;height:32px;background:none;border:1px solid var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0;padding:0}
.btn-star:hover,.btn-star.saved{border-color:var(--orange);color:var(--orange)}
.btn-del-brand{width:28px;height:28px;background:none;border:1px solid var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-size:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0}
.btn-del-brand:hover{background:var(--red-bg);color:var(--red);border-color:var(--red-border)}
.btn-add-brand{display:flex;align-items:center;gap:8px;width:100%;padding:10px 14px;background:none;border:1px dashed var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all .2s}
.btn-add-brand:hover{border-color:rgba(21,64,240,.4);color:var(--blue);background:rgba(21,64,240,.06)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Favorites Ã¢â€â‚¬Ã¢â€â‚¬ */
.fav-grid{display:flex;flex-wrap:wrap;gap:8px;min-height:32px;margin-bottom:12px}
.fav-chip{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;background:rgba(21,64,240,.1);border:1px solid rgba(21,64,240,.25);border-radius:20px;font-size:11px;font-weight:600;color:var(--text);cursor:pointer;transition:all .2s}
.fav-chip:hover{background:var(--blue);color:#fff;border-color:var(--blue)}
.fav-chip-del{color:var(--muted);cursor:pointer;font-size:13px;margin-left:2px;line-height:1}
.fav-chip-del:hover{color:var(--red)}
.fav-empty{font-size:12px;color:var(--muted2);padding:4px 0;font-style:italic}
.session-btns{display:flex;gap:8px;flex-wrap:wrap}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Buttons Ã¢â€â‚¬Ã¢â€â‚¬ */
.btn-primary{width:100%;padding:15px;background:var(--blue);border:none;border-radius:var(--radius-sm);color:#fff;font-family:var(--mono);font-size:12px;font-weight:600;letter-spacing:3px;text-transform:uppercase;cursor:pointer;transition:all .2s;position:relative;overflow:hidden}
.btn-primary::before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent);transform:translateX(-100%);transition:.5s}
.btn-primary:hover{background:var(--blue-hover)}
.btn-primary:hover::before{transform:translateX(100%)}
.btn-primary:active{transform:scale(.99)}
.btn-primary:disabled{opacity:.4;cursor:not-allowed}
.btn-secondary{padding:9px 16px;background:transparent;border:1px solid var(--border2);border-radius:var(--radius-sm);color:var(--text2);font-size:12px;font-weight:600;letter-spacing:1px;text-transform:uppercase;cursor:pointer;transition:all .2s}
.btn-secondary:hover{border-color:var(--blue);color:var(--blue)}
.btn-sm{padding:7px 14px;background:var(--blue);border:none;border-radius:var(--radius-sm);color:#fff;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:background .2s}
.btn-sm:hover{background:var(--blue-hover)}
.btn-sm.outline{background:transparent;border:1px solid var(--border2);color:var(--text2)}
.btn-sm.outline:hover{border-color:var(--blue);color:var(--blue)}
.btn-danger-sm{padding:7px 14px;background:transparent;border:1px solid var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all .2s}
.btn-danger-sm:hover{background:var(--red-bg);color:var(--red);border-color:var(--red-border)}
.spinner{display:inline-block;width:12px;height:12px;border:2px solid rgba(255,255,255,.35);border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;margin-right:8px;vertical-align:middle}
@keyframes spin{to{transform:rotate(360deg)}}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Class mode buttons Ã¢â€â‚¬Ã¢â€â‚¬ */
.class-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:12px}
.mode-btn{padding:11px 8px;background:#fff;border:1.5px solid var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;text-align:center;transition:all .2s}
.mode-btn:hover{border-color:var(--blue);color:var(--blue)}
.mode-btn.active{background:var(--blue);border-color:var(--blue);color:#fff}
.mode-sub{font-size:9px;display:block;opacity:.65;margin-top:3px;letter-spacing:1px;font-weight:400}
.manual-wrap{display:none;margin-top:12px;padding:14px;background:var(--surface2);border-radius:var(--radius-sm);border:1px solid var(--border)}
.manual-wrap.show{display:block}
.cls-add-row{display:flex;gap:8px;align-items:center;margin-bottom:10px}
.cls-num-input{width:80px;padding:9px 12px;background:var(--blue);border:none;border-radius:var(--radius-sm);color:#fff;font-family:var(--mono);font-size:16px;font-weight:600;text-align:center;outline:none;-moz-appearance:textfield}
.cls-num-input::-webkit-outer-spin-button,.cls-num-input::-webkit-inner-spin-button{-webkit-appearance:none}
.cls-num-input::placeholder{color:rgba(255,255,255,.5);font-size:12px}
.btn-agregar-clase{padding:9px 16px;background:var(--blue);border:none;border-radius:var(--radius-sm);color:#fff;font-family:var(--mono);font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:background .2s}
.btn-agregar-clase:hover{background:var(--blue-hover)}
.cls-clear-btn{background:none;border:none;color:var(--muted);font-size:11px;cursor:pointer;text-decoration:underline;padding:4px}
.cls-chips-area{display:flex;flex-wrap:wrap;gap:6px;min-height:30px}
.cls-chips-area.empty::before{content:'Sin clases seleccionadas';font-size:11px;color:var(--muted2);font-style:italic}
.cls-chip{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;background:var(--blue);border-radius:20px;font-family:var(--mono);font-size:11px;font-weight:600;color:#fff}
.cls-chip-del{cursor:pointer;opacity:.7;font-size:13px;line-height:1}
.cls-chip-del:hover{opacity:1}
.cls-dup-warn{font-size:11px;color:var(--red);margin-top:6px;display:none}
.cls-dup-warn.show{display:block}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Per-brand class toggle Ã¢â€â‚¬Ã¢â€â‚¬ */
.pbmode-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.btn-pbmode{display:inline-flex;align-items:center;gap:6px;padding:7px 14px;background:#fff;border:1.5px solid var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all .2s}
.btn-pbmode:hover,.btn-pbmode.active{border-color:var(--blue);color:var(--blue);background:var(--blue-light)}
.pb-classes-wrap{display:none}
.pb-classes-wrap.show{display:block;animation:fadeUp .2s ease}
.pb-brand-row{border:1px solid var(--border);border-radius:var(--radius-sm);margin-bottom:8px;overflow:hidden}
.pb-brand-hdr{display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--surface2);cursor:pointer;border-bottom:1px solid transparent;transition:all .2s}
.pb-brand-hdr:hover{background:var(--sky)}
.pb-brand-body{display:none;padding:14px;border-top:1px solid var(--border)}
.pb-brand-body.open{display:block}
.pb-brand-num{width:20px;height:20px;border-radius:50%;background:var(--blue);color:#fff;font-family:var(--mono);font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.pb-brand-name{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--text);flex:1}
.pb-summary{font-size:11px;color:var(--muted);flex-shrink:0}
.pb-summary.has{color:var(--green)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Toggles Ã¢â€â‚¬Ã¢â€â‚¬ */
.toggles-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.tog{display:flex;align-items:center;gap:10px;cursor:pointer;user-select:none;padding:12px 14px;border:1.5px solid var(--border);border-radius:var(--radius-sm);background:#fff;transition:border-color .2s}
.tog:hover{border-color:var(--blue)}
.tog input{display:none}
.tog-label{font-size:12px;color:var(--text2);font-weight:500;flex:1}
.track{width:36px;height:20px;background:var(--border2);border-radius:10px;position:relative;transition:background .2s;flex-shrink:0}
.track::after{content:'';position:absolute;top:3px;left:3px;width:14px;height:14px;background:var(--muted);border-radius:50%;transition:transform .2s,background .2s}
.tog input:checked~.track{background:var(--blue)}
.tog input:checked~.track::after{transform:translateX(16px);background:#fff}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Criteria config Ã¢â€â‚¬Ã¢â€â‚¬ */
.cfg-btns{display:flex;gap:8px;margin-bottom:14px}
.cfg-btn{flex:1;padding:10px;background:#fff;border:1.5px solid var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all .2s;text-align:center}
.cfg-btn:hover{border-color:var(--blue);color:var(--blue)}
.cfg-btn.active{background:var(--blue);border-color:var(--blue);color:#fff}
.sliders-wrap{display:none;margin-top:4px}
.sliders-wrap.show{display:block;animation:fadeUp .2s ease}
.slider-row{display:grid;grid-template-columns:28px 1fr auto;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--border)}
.slider-row:last-of-type{border-bottom:none}
.sl-badge{width:28px;height:28px;min-width:28px;border-radius:50%;background:var(--blue);color:#fff;font-family:var(--mono);font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;line-height:1;text-align:center}
.sl-info{display:flex;flex-direction:column;gap:2px}
.sl-name{font-size:12px;font-weight:600;color:var(--text)}
.sl-desc{font-size:10px;color:var(--muted)}
input[type=range]{-webkit-appearance:none;width:100%;height:4px;background:var(--border2);border-radius:2px;outline:none;cursor:pointer;margin-top:6px}
input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:var(--blue);cursor:pointer;border:2px solid #fff;box-shadow:var(--shadow-sm)}
.sl-val{font-family:var(--mono);font-size:12px;font-weight:700;color:var(--blue);background:var(--blue-light);border:1px solid var(--blue-mid);border-radius:var(--radius-sm);padding:3px 8px;white-space:nowrap}
.crit-thresh{display:flex;align-items:center;gap:12px;padding:10px 0 0}
.crit-thresh-label{font-size:11px;color:var(--text2);flex:1}
.stepper{display:flex;align-items:center;gap:8px}
.step-btn{width:26px;height:26px;border-radius:50%;background:var(--blue);border:none;color:#fff;font-size:14px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .2s}
.step-btn:hover{background:var(--blue-hover)}
.step-val{font-family:var(--mono);font-size:16px;font-weight:700;color:var(--navy);min-width:20px;text-align:center}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Niza link button Ã¢â€â‚¬Ã¢â€â‚¬ */
.niza-btn{display:flex;align-items:center;justify-content:center;gap:8px;width:100%;padding:11px;background:#fff;border:1.5px solid var(--blue-mid);border-radius:var(--radius-sm);color:var(--blue);font-size:12px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;text-decoration:none;transition:all .2s;margin-bottom:14px}
.niza-btn:hover{background:var(--blue);color:#fff;border-color:var(--blue);box-shadow:var(--shadow)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Progress bar Ã¢â€â‚¬Ã¢â€â‚¬ */
.prog-wrap{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:18px 22px;margin-bottom:20px;display:none}
.prog-wrap.show{display:block;animation:fadeUp .3s ease}
.prog-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.prog-label{font-size:12px;color:var(--text);font-weight:600;font-family:var(--mono);letter-spacing:.5px}
.prog-eta{font-size:10px;color:var(--muted);font-family:var(--mono)}
.prog-track{height:6px;background:var(--border2);border-radius:3px;overflow:hidden;margin-bottom:10px}
.prog-bar{height:100%;width:0%;background:linear-gradient(90deg,#3b82f6,#60a5fa);border-radius:3px;transition:width .7s cubic-bezier(.4,0,.2,1)}
.prog-detail{font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.prog-steps{display:flex;gap:5px;flex-wrap:wrap}
.step-pill{font-size:9px;font-weight:600;letter-spacing:1px;text-transform:uppercase;padding:3px 9px;border-radius:20px;border:1px solid;transition:all .3s}
.step-pill.pending{border-color:rgba(255,255,255,.15);color:rgba(255,255,255,.3)}
.step-pill.active{border-color:#60a5fa;color:#93c5fd;background:rgba(96,165,250,.12);animation:pulse 1.2s infinite}
.step-pill.done{border-color:rgba(74,222,128,.4);color:#4ade80;background:rgba(74,222,128,.08)}
.step-pill.error{border-color:rgba(248,113,113,.4);color:#f87171}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Results area Ã¢â€â‚¬Ã¢â€â‚¬ */
#results-area{display:none;margin-top:8px}
#results-area.show{display:block}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Brand result tabs Ã¢â€â‚¬Ã¢â€â‚¬ */
.brand-tabs-bar{display:flex;gap:0;border-bottom:2px solid var(--border);overflow-x:auto;scrollbar-width:none;margin-bottom:0}
.brand-tabs-bar::-webkit-scrollbar{display:none}
.btab{flex-shrink:0;display:flex;align-items:center;gap:8px;padding:10px 20px;font-size:12px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--muted);border-bottom:2px solid transparent;margin-bottom:-2px;cursor:pointer;transition:all .2s;white-space:nowrap;background:transparent;border-left:none;border-right:none;border-top:none}
.btab:hover{color:var(--navy);background:var(--surface2)}
.btab.active{color:var(--blue);border-bottom-color:var(--blue);background:var(--blue-light)}
.btab.compare{border-left:2px solid var(--border);margin-left:8px}
.btab-dot{width:8px;height:8px;border-radius:50%;background:var(--border2);flex-shrink:0;transition:all .3s}
.btab-dot.running{background:var(--blue);animation:pulse 1s infinite}
.btab-dot.ok{background:var(--green)}
.btab-dot.err{background:var(--red)}
.btab-content{display:none;animation:fadeUp .3s ease}
.btab-content.active{display:block}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Per-brand analysis accordion Ã¢â€â‚¬Ã¢â€â‚¬ */
.analysis-accordion{border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;margin-bottom:12px}
.aa-header{display:flex;align-items:center;gap:12px;padding:14px 18px;background:var(--surface2);cursor:pointer;border-bottom:1px solid transparent;transition:all .2s;user-select:none}
.aa-header:hover{background:var(--surface)}
.aa-header.open{background:rgba(21,64,240,.06);border-bottom:1px solid var(--border)}
.aa-icon{width:32px;height:32px;border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;background:var(--surface);border:1px solid var(--border2)}
.aa-header.open .aa-icon{background:var(--blue);border-color:var(--blue)}
.aa-title{font-size:13px;font-weight:600;color:var(--text);flex:1}
.aa-subtitle{font-size:11px;color:var(--muted)}
.aa-status-badge{font-family:var(--mono);font-size:10px;font-weight:600;padding:3px 10px;border-radius:20px;border:1px solid;white-space:nowrap}
.aa-chevron{color:var(--muted);transition:transform .2s;font-size:12px;flex-shrink:0}
.aa-header.open .aa-chevron{transform:rotate(180deg)}
.aa-body{display:none;padding:18px}
.aa-body.open{display:block;animation:fadeUp .25s ease}
.aa-hint{font-size:11px;color:var(--muted);text-align:center;padding:6px 0 2px;font-style:italic}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Result sections (inside accordion) Ã¢â€â‚¬Ã¢â€â‚¬ */
.rs{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);margin-bottom:12px;overflow:hidden}
.rs-hdr{display:flex;align-items:center;gap:10px;padding:12px 16px;background:var(--surface);border-bottom:1px solid var(--border);flex-wrap:wrap}
.rs-icon{width:28px;height:28px;border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0}
.rs-title{font-size:13px;font-weight:600;color:var(--text);flex:1}
.rs-count{font-family:var(--mono);font-size:10px;color:var(--muted);background:var(--surface2);border:1px solid var(--border);padding:2px 8px;border-radius:20px;white-space:nowrap}
.rs-actions{display:flex;gap:6px;margin-left:auto}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Tables Ã¢â€â‚¬Ã¢â€â‚¬ */
.tbl-wrap{overflow-x:auto;max-height:400px;overflow-y:auto}
table{width:100%;border-collapse:collapse}
thead th{background:#e8e8e8;position:sticky;top:0;z-index:2;padding:9px 12px;font-size:9px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:rgba(0,0,0,.5);border-bottom:1px solid var(--border2);text-align:left;white-space:nowrap;font-family:var(--mono)}
tbody tr{transition:background .1s}
tbody tr:hover{background:rgba(21,64,240,.04)}
tbody tr:nth-child(even){background:rgba(0,0,0,.02)}
td{padding:9px 12px;font-size:12px;border-bottom:1px solid var(--border);vertical-align:middle;color:var(--text2)}
td.mono{font-family:var(--mono)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Chips Ã¢â€â‚¬Ã¢â€â‚¬ */
.chip{display:inline-block;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:600;font-family:var(--mono);letter-spacing:.5px}
.chip-red{background:var(--red-bg);color:var(--red);border:1px solid var(--red-border)}
.chip-orange{background:#fff7ed;color:var(--orange);border:1px solid #fed7aa}
.chip-blue{background:var(--blue-light);color:var(--blue);border:1px solid var(--blue-mid)}
.chip-green{background:var(--green-bg);color:var(--green);border:1px solid var(--green-border)}
.chip-muted{background:var(--surface2);color:var(--muted);border:1px solid var(--border)}
.tag-ok{background:var(--green-bg);color:var(--green);border:1px solid var(--green-border);font-size:10px;padding:2px 8px;border-radius:20px;font-weight:600;white-space:nowrap}
.tag-nok{background:var(--red-bg);color:var(--red);border:1px solid var(--red-border);font-size:10px;padding:2px 8px;border-radius:20px;font-weight:600;white-space:nowrap}
.tag-warn{background:#fff7ed;color:var(--orange);border:1px solid #fed7aa;font-size:10px;padding:2px 8px;border-radius:20px;font-weight:600;white-space:nowrap}
.empty-state{padding:40px;text-align:center;color:var(--muted2);font-size:12px;letter-spacing:1px;text-transform:uppercase}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Stats KPI strip Ã¢â€â‚¬Ã¢â€â‚¬ */
.kpi-strip{display:flex;gap:0;border-radius:var(--radius);overflow:hidden;margin-bottom:16px;background:#f0f0f0;border:1px solid var(--border);box-shadow:var(--shadow)}
.kpi-item{flex:1;text-align:center;padding:16px 10px;border-right:1px solid var(--border)}
.kpi-item:last-child{border-right:none}
.kpi-label{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:rgba(0,0,0,.45);font-family:var(--mono);margin-bottom:6px}
.kpi-num{font-family:var(--mono);font-size:22px;font-weight:700;color:#1a1a1a;line-height:1}
.kpi-num.blue{color:#60a5fa}
.kpi-num.purple{color:#a78bfa}
.kpi-num.red{color:#f87171}
.kpi-num.orange{color:#fb923c}
.kpi-num.green{color:#4ade80}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Per-class stats Ã¢â€â‚¬Ã¢â€â‚¬ */
.cls-toggle-btn{width:100%;display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);cursor:pointer;font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);transition:all .2s;margin-top:14px}
.cls-toggle-btn:hover{border-color:var(--blue);color:var(--blue)}
.cls-toggle-btn.open{border-color:var(--blue);color:var(--blue);background:var(--blue-light)}
.cls-charts-grid{display:none;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin-top:12px}
.cls-charts-grid.open{display:grid}
.cls-stat-card{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:14px}
.cls-chart-canvas{position:relative;height:130px}
.cls-kpis{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.cls-kpi{flex:1;min-width:60px;text-align:center;background:#fff;border:1px solid var(--border);border-radius:var(--radius-sm);padding:6px}
.cls-kpi-num{font-family:var(--mono);font-size:16px;font-weight:700;color:var(--navy)}
.cls-kpi-num.r{color:var(--red)}
.cls-kpi-num.g{color:var(--green)}
.cls-kpi-lbl{font-size:9px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-top:2px}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Conflict ticker Ã¢â€â‚¬Ã¢â€â‚¬ */
.cls-ticker-wrap{overflow:hidden}
.cls-ticker-controls{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:var(--surface2);border-bottom:1px solid var(--border)}
.cls-ticker-info{font-size:10px;color:var(--muted);letter-spacing:.5px}
.cls-ticker-btns{display:flex;gap:6px}
.btn-ticker{padding:5px 10px;background:#fff;border:1.5px solid var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-size:12px;cursor:pointer;transition:all .2s}
.btn-ticker:hover{border-color:var(--blue);color:var(--blue)}
.btn-ver-todos{padding:5px 12px;background:var(--blue);border:none;border-radius:var(--radius-sm);color:#fff;font-size:10px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:background .2s}
.btn-ver-todos:hover{background:var(--blue-hover)}
.cls-ticker-viewport{overflow:hidden;padding:12px}
.cls-ticker-track{display:flex;gap:10px;transition:transform .4s cubic-bezier(.4,0,.2,1)}
.cls-mini-card{flex-shrink:0;border-radius:var(--radius-sm);padding:14px;border:1.5px solid var(--border);background:#fff;min-width:calc(33.33% - 7px)}
.cls-mini-card.nok{border-color:var(--red-border);background:var(--red-bg)}
.cls-mini-card.ok{border-color:var(--green-border);background:var(--green-bg)}
.cmc-clase{font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);font-weight:600}
.cmc-num{font-family:var(--mono);font-size:28px;font-weight:700;color:var(--navy);margin:4px 0}
.cmc-status{font-size:11px;font-weight:600;letter-spacing:1px}
.cmc-status.nok{color:var(--red)}.cmc-status.ok{color:var(--green)}
.cmc-count{font-size:10px;color:var(--muted);margin-top:4px}
.cls-ticker-dots{display:flex;gap:6px;justify-content:center;padding:8px}
.t-dot{width:6px;height:6px;border-radius:50%;background:var(--border2);cursor:pointer;transition:all .2s}
.t-dot.active{background:var(--blue);transform:scale(1.3)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Conflict status bar Ã¢â€â‚¬Ã¢â€â‚¬ */
.conf-status-bar{display:none;padding:10px 16px;border-bottom:1px solid var(--border);align-items:center;gap:10px;background:var(--surface2)}
.conf-status-bar.show{display:flex}
.cgs-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.cgs-dot.ok{background:var(--green);box-shadow:0 0 6px rgba(22,163,74,.4)}
.cgs-dot.nok{background:var(--red);box-shadow:0 0 6px rgba(220,38,38,.4)}
.cgs-text{font-size:12px;font-weight:600;font-family:var(--mono)}
.cgs-text.ok{color:var(--green)}.cgs-text.nok{color:var(--red)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Single class card Ã¢â€â‚¬Ã¢â€â‚¬ */
.cls-card-single{border-radius:var(--radius-sm);padding:16px;border:1.5px solid}
.cls-card-single.ok{border-color:var(--green-border);background:var(--green-bg)}
.cls-card-single.nok{border-color:var(--red-border);background:var(--red-bg)}
.cls-card-hdr{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.cls-badge{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:1.5px;padding:3px 10px;border-radius:20px;background:var(--blue);color:#fff}
.cls-marks-table{width:100%;border-collapse:collapse;margin-top:8px}
.cls-marks-table th{padding:6px 10px;font-size:9px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);text-align:left;border-bottom:1px solid var(--border)}
.cls-marks-table td{padding:7px 10px;font-size:11px;border-bottom:1px solid var(--border);color:var(--text2)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Ver todos modal Ã¢â€â‚¬Ã¢â€â‚¬ */
.modal-back{display:none;position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:1000;backdrop-filter:blur(3px);align-items:center;justify-content:center}
.modal-back.show{display:flex;animation:fadeIn .2s}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.modal-box{background:#fff;border-radius:var(--radius);max-width:800px;width:95%;max-height:90vh;overflow-y:auto;padding:28px;position:relative;box-shadow:var(--shadow-md)}
.modal-close{position:absolute;top:14px;right:16px;background:none;border:none;color:var(--muted);font-size:20px;cursor:pointer;transition:color .2s;line-height:1}
.modal-close:hover{color:var(--navy)}
.modal-title{font-size:18px;font-weight:700;color:var(--navy);margin-bottom:4px}
.modal-sub{font-size:11px;color:var(--muted);margin-bottom:20px;letter-spacing:.5px}
.vt-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.vt-class-block{border:1.5px solid;border-radius:var(--radius-sm);padding:14px}
.vt-class-block.ok{border-color:var(--green-border);background:var(--green-bg)}
.vt-class-block.nok{border-color:var(--red-border);background:var(--red-bg)}
.vt-class-hdr{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.vt-cls-status{font-size:11px;font-weight:600}
.vt-cls-status.ok{color:var(--green)}.vt-cls-status.nok{color:var(--red)}
.vt-table th,.vt-table td{padding:5px 8px;font-size:10px}
.vt-empty{font-size:11px;color:var(--green);font-style:italic;padding:6px 0}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Criteria modal Ã¢â€â‚¬Ã¢â€â‚¬ */
.crit-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px}
.crit-card{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px}
.crit-num{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--blue);margin-bottom:4px}
.crit-name{font-size:12px;font-weight:600;color:var(--navy);margin-bottom:4px}
.crit-val{font-family:var(--mono);font-size:13px;font-weight:700;color:var(--navy2);margin-bottom:6px}
.crit-desc{font-size:11px;color:var(--muted);line-height:1.5}
.concesion-rule{background:var(--blue-light);border:1px solid var(--blue-mid);border-radius:var(--radius-sm);padding:14px;font-size:12px;color:var(--navy2)}
.rule-hl{font-weight:700;color:var(--blue)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Social / Domain / MUA tool results Ã¢â€â‚¬Ã¢â€â‚¬ */
.avail-pill{display:inline-flex;align-items:center;gap:4px;font-size:10px;font-weight:600;letter-spacing:.5px;padding:3px 10px;border-radius:20px;border:1px solid}
.avail-pill.ok{background:var(--green-bg);border-color:var(--green-border);color:var(--green)}
.avail-pill.taken{background:var(--red-bg);border-color:var(--red-border);color:var(--red)}
.avail-pill.unknown{background:var(--surface2);border-color:var(--border2);color:var(--muted)}
.tool-result-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-top:12px}
.tool-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius-sm);padding:12px;transition:box-shadow .2s}
.tool-card:hover{box-shadow:var(--shadow)}
.tc-platform{font-size:9px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.tc-url{font-size:10px;color:var(--muted2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-top:4px}
.tc-url a{color:var(--blue);text-decoration:none}
.tc-url a:hover{text-decoration:underline}
.domain-card{display:flex;align-items:center;gap:12px;padding:12px 14px;background:#fff;border:1px solid var(--border);border-radius:var(--radius-sm);transition:box-shadow .2s}
.domain-card:hover{box-shadow:var(--shadow)}
.domain-name{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--navy);flex:1}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Compare section Ã¢â€â‚¬Ã¢â€â‚¬ */
.compare-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.cmp-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow-sm)}
.cmp-brand{font-family:var(--mono);font-size:14px;font-weight:700;color:var(--navy);margin-bottom:4px;display:flex;align-items:center;gap:8px}
.cmp-meta{font-size:11px;color:var(--muted);margin-bottom:14px}
.cmp-kpis{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.cmp-kpi{flex:1;min-width:60px;text-align:center;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:8px}
.cmp-kpi-num{font-family:var(--mono);font-size:18px;font-weight:700;color:var(--navy)}
.cmp-kpi-num.r{color:var(--red)}.cmp-kpi-num.g{color:var(--green)}
.cmp-kpi-lbl{font-size:9px;color:var(--muted);letter-spacing:1px;text-transform:uppercase}
.cmp-drill-btn{width:100%;display:flex;align-items:center;gap:8px;margin-top:12px;padding:8px 12px;background:var(--surface2);border:1.5px dashed var(--border2);border-radius:var(--radius-sm);color:var(--muted);font-size:10px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;cursor:pointer;transition:all .2s}
.cmp-drill-btn:hover{border-color:var(--blue);color:var(--blue);border-style:solid}
.cmp-drill-body{display:none;margin-top:10px;border-top:1px solid var(--border);padding-top:10px}
.cmp-drill-body.open{display:block}
.cmp-cls-row{display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid var(--border)}
.cmp-cls-row:last-child{border-bottom:none}
.cmp-cls-badge{font-family:var(--mono);font-size:9px;font-weight:600;padding:2px 8px;border-radius:20px;background:var(--blue);color:#fff;flex-shrink:0}
.cmp-bar-wrap{flex:1;height:6px;background:var(--border2);border-radius:3px;overflow:hidden}
.cmp-bar-fill{height:100%;border-radius:3px}
.cmp-bar-fill.ok{background:var(--green)}.cmp-bar-fill.nok{background:var(--red)}
.cmp-pct{font-family:var(--mono);font-size:10px;font-weight:600;min-width:36px;text-align:right}
.cmp-count{font-size:9px;color:var(--muted);min-width:52px;text-align:right}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Registration Gate Ã¢â€â‚¬Ã¢â€â‚¬ */
.reg-gate{position:fixed;inset:0;background:rgba(10,10,20,.75);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);z-index:99999;display:flex;align-items:center;justify-content:center;padding:16px}
.reg-gate.done{display:none!important}
.reg-box{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 32px 100px rgba(0,0,0,.4);max-width:680px;width:100%;max-height:92vh;display:flex;flex-direction:column}
.reg-box-hdr{background:#1540F0;padding:22px 28px;flex-shrink:0}
.reg-box-title{font-family:Georgia,'Times New Roman',serif;font-size:28px;font-style:italic;color:#fff;margin-bottom:6px;line-height:1}
.reg-box-title span{font-family:'Courier New',Courier,monospace;font-style:normal;font-size:15px;font-weight:700;background:rgba(255,255,255,.15);border-radius:4px;padding:2px 8px;margin-left:5px;vertical-align:middle}
.reg-box-sub{font-size:10px;color:rgba(255,255,255,.65);letter-spacing:2.5px;text-transform:uppercase;font-family:'Courier New',monospace}
.reg-box-body{flex:1;overflow-y:auto;position:relative;min-height:200px}
.reg-box-body::-webkit-scrollbar{width:5px}
.reg-box-body::-webkit-scrollbar-thumb{background:#ccc;border-radius:3px}
.reg-loading{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#f5f5f5;gap:14px;transition:opacity .4s;z-index:2}
.reg-loading.hidden{opacity:0;pointer-events:none}
.reg-spin{width:34px;height:34px;border:3px solid rgba(21,64,240,.2);border-top-color:#1540F0;border-radius:50%;animation:spin .7s linear infinite}
.reg-load-txt{font-size:11px;color:#888;letter-spacing:2px;text-transform:uppercase;font-family:'Courier New',monospace}
.reg-iframe{width:100%;border:none;display:block;min-height:1800px}
.reg-thanks{display:none;flex-direction:column;align-items:center;justify-content:center;padding:56px 32px;text-align:center;gap:18px}
.reg-thanks.show{display:flex}
.reg-check-circle{width:64px;height:64px;border-radius:50%;background:rgba(34,197,94,.12);border:2px solid #22c55e;display:flex;align-items:center;justify-content:center;font-size:28px;color:#22c55e;flex-shrink:0}
.reg-thanks-title{font-size:22px;font-weight:700;color:#1a1a1a}
.reg-thanks-sub{font-size:13px;color:#666;line-height:1.7;max-width:360px}
.reg-btn-enter{padding:15px 44px;background:#1540F0;border:none;border-radius:6px;color:#fff;font-family:'Courier New',monospace;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;cursor:pointer;transition:background .2s;margin-top:4px}
.reg-btn-enter:hover{background:#0f34cc}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Toast Ã¢â€â‚¬Ã¢â€â‚¬ */
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(12px);background:#1a1a1a;border:1px solid var(--border2);color:#fff;font-size:12px;font-weight:500;padding:10px 20px;border-radius:var(--radius-sm);z-index:9999;opacity:0;transition:all .3s;pointer-events:none;white-space:nowrap;box-shadow:var(--shadow-md)}
.toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
.toast.info{background:#111;border-color:var(--blue)}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Misc Ã¢â€â‚¬Ã¢â€â‚¬ */
.section-label{font-size:10px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;gap:10px;margin-bottom:16px}
.section-label::after{content:'';flex:1;height:1px;background:var(--border)}
.stat-pill{text-align:center;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);padding:6px 14px}
.stat-num{font-family:var(--mono);font-size:20px;color:var(--navy);line-height:1;font-weight:700}
.stat-lbl{font-size:9px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-top:2px}
.export-row{display:flex;justify-content:flex-end;gap:8px;margin-bottom:14px}
.chart-canvas-rel{position:relative;height:180px}

/* Per-brand in class mode */
.pb-mode-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:10px}

/* Ã¢â€â‚¬Ã¢â€â‚¬ 2Ãƒâ€”2 Results Grid Ã¢â€â‚¬Ã¢â€â‚¬ */
.results-grid-2x2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px;align-items:start}
@media(max-width:900px){.results-grid-2x2{grid-template-columns:1fr}}
.result-panel{background:#fff;border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}
.result-panel-hdr{display:flex;align-items:center;gap:10px;padding:12px 16px;background:var(--surface2);border-bottom:1px solid var(--border);flex-shrink:0}
.result-panel-title{font-size:11px;font-weight:700;color:var(--text);flex:1;letter-spacing:1.5px;text-transform:uppercase}
.result-panel-body{padding:14px;overflow-y:auto;flex:1}
.result-panel-body::-webkit-scrollbar{width:4px}
.result-panel-body::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Auth Panel Ã¢â€â‚¬Ã¢â€â‚¬ */
.auth-panel{position:fixed;top:64px;right:20px;z-index:9999;background:#ffffff;border:1px solid var(--border2);border-radius:var(--radius);padding:18px;box-shadow:var(--shadow-md);width:290px;transition:all .3s}
.auth-panel.hidden{display:none}
.auth-panel-title{font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:14px;display:flex;align-items:center;justify-content:space-between}
.auth-close{background:none;border:none;color:var(--muted);font-size:18px;cursor:pointer;line-height:1;padding:0}
.auth-close:hover{color:var(--text)}
.auth-input{width:100%;padding:10px 12px;border:1px solid var(--border2);border-radius:var(--radius-sm);font-size:13px;color:var(--text);background:var(--surface2);outline:none;transition:border-color .2s;margin-bottom:8px}
.auth-input:focus{border-color:var(--blue)}
.auth-btns{display:flex;gap:8px;margin-top:4px}
.auth-msg{font-size:11px;color:var(--muted);margin-top:8px;line-height:1.5}
.auth-msg.err{color:var(--red)}
.auth-msg.ok{color:var(--green)}
.auth-user-info{font-size:12px;color:var(--text2);margin-bottom:12px;padding:8px;background:var(--surface2);border-radius:var(--radius-sm)}
.auth-user-email{font-weight:600;color:var(--text);font-size:13px;word-break:break-all}
.auth-user-role{font-size:10px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-top:2px}
/* Ã¢â€â‚¬Ã¢â€â‚¬ SIGA Period Banner Ã¢â€â‚¬Ã¢â€â‚¬ */
.siga-period-banner{display:flex;align-items:center;gap:10px;padding:10px 16px;background:linear-gradient(135deg,#fef9c3,#fef3c7);border:1px solid #fde68a;border-radius:var(--radius-sm);margin-bottom:14px;flex-wrap:wrap}
.siga-period-icon{font-size:16px;flex-shrink:0}
.siga-period-label{font-size:11px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#92400e;flex-shrink:0}
.siga-period-range{font-family:var(--mono);font-size:12px;font-weight:600;color:#1f2937;background:#fff;padding:3px 10px;border-radius:4px;border:1px solid #fde68a}
.siga-period-dias{font-size:11px;color:#78716c;margin-left:auto}
.btn-auth{padding:7px 16px;background:transparent;border:1px solid rgba(255,255,255,.55);color:#ffffff;font-family:var(--mono);font-size:10px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;border-radius:var(--radius-sm);cursor:pointer;transition:all .2s}
.btn-auth:hover{background:rgba(255,255,255,.12);border-color:#ffffff}
.btn-auth.logged{background:rgba(34,197,94,.2);border-color:rgba(34,197,94,.5);color:#86efac}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Nota Legal Ã¢â€â‚¬Ã¢â€â‚¬ */
.nota-legal-wrap{margin-bottom:24px;border:1px solid var(--border2);border-radius:var(--radius-sm);overflow:hidden}
.nota-legal-toggle{width:100%;display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:var(--surface2);border:none;cursor:pointer;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);transition:background .2s}
.nota-legal-toggle:hover{background:var(--surface)}
.nota-legal-chevron{transition:transform .25s;font-size:12px}
.nota-legal-chevron.open{transform:rotate(90deg)}
.nota-legal-body{display:none;padding:14px 16px;background:#fff;border-top:1px solid var(--border);font-size:12px;color:var(--text2);line-height:1.75}
.nota-legal-body.open{display:block;animation:fadeUp .2s ease}
.nota-legal-body p{margin-bottom:8px}
.nota-legal-body p:last-child{margin-bottom:0}
.nota-legal-body a{color:var(--blue);text-decoration:none;word-break:break-all}
.nota-legal-body a:hover{text-decoration:underline}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Responsive: tablet Ã¢â€â‚¬Ã¢â€â‚¬ */
@media(max-width:768px){
  .topbar{padding:0 14px;height:56px}
  .topbar-logo{position:static;transform:none;margin:0 auto}
  .btn-nuevo{font-size:9px;letter-spacing:1px;padding:6px 10px}
  .main{padding:20px 14px 60px}
  .wiz-bar{padding:0 8px;margin-bottom:24px}
  .wiz-bar::before{top:14px;left:calc(8px + 40px);right:calc(8px + 40px)}
  .wiz-fill{top:14px;left:calc(8px + 40px)}
  .wiz-circle{width:28px;height:28px;font-size:11px}
  .wiz-label{font-size:8px;letter-spacing:.5px}
  .class-grid{grid-template-columns:repeat(2,1fr)}
  .toggles-grid{grid-template-columns:1fr}
  .kpi-strip{flex-wrap:wrap}
  .kpi-item{flex:1 1 40%}
  .vt-grid{grid-template-columns:1fr}
  .crit-grid{grid-template-columns:1fr}
  .pb-mode-grid{grid-template-columns:repeat(2,1fr)}
  .auth-panel{width:calc(100% - 32px);right:16px;top:56px}
  .cls-mini-card{min-width:calc(50% - 5px)}
  .giro-grid{grid-template-columns:1fr}
  .compare-grid{grid-template-columns:1fr}
  .modal-box{padding:18px}
  .analysis-types{grid-template-columns:1fr 1fr}
  .cfg-btns{flex-wrap:wrap}
  .slider-row{grid-template-columns:28px 1fr auto;gap:8px}
  .brand-tabs-bar .btab{padding:10px 14px;font-size:11px}
  .export-row{flex-wrap:wrap;justify-content:flex-start}
}

/* Ã¢â€â‚¬Ã¢â€â‚¬ Responsive: mÃƒÂ³vil Ã¢â€â‚¬Ã¢â€â‚¬ */
@media(max-width:480px){
  .topbar{height:auto;padding:10px 12px;flex-wrap:nowrap;gap:8px}
  .topbar-logo{position:static;transform:none;flex:1;justify-content:center}
  .wordmark{font-size:24px}
  .logo-divider{height:26px;margin:0 10px}
  .tm-trademark,.tm-insights,.tm-mexico{font-size:10px}
  .topbar-spacer{display:none}
  .btn-nuevo{font-size:8px;letter-spacing:.5px;padding:6px 10px;white-space:nowrap}
  .main{padding:14px 10px 60px}
  .wiz-label{display:none}
  .wiz-circle{width:26px;height:26px;font-size:10px}
  .card{padding:14px}
  .analysis-types{grid-template-columns:1fr}
  .class-grid{grid-template-columns:repeat(2,1fr)}
  .kpi-strip{flex-direction:column}
  .kpi-item{flex:1 1 100%;border-right:none;border-bottom:1px solid var(--border)}
  .kpi-item:last-child{border-bottom:none}
  .modal-box{padding:14px;width:100%;max-height:95vh}
  .cls-mini-card{min-width:calc(100% - 0px)}
  .giro-grid{grid-template-columns:1fr}
  .reg-box-title{font-size:22px}
  .brand-tabs-bar .btab{padding:8px 10px;font-size:10px}
  .aa-header{padding:12px 14px}
  .aa-body{padding:12px}
  .wiz-bar{padding:0 4px}
  .wiz-bar::before{left:calc(4px + 36px);right:calc(4px + 36px)}
  .wiz-fill{left:calc(4px + 36px)}
  .tbl-wrap{max-height:320px}
  .slider-row{grid-template-columns:1fr;gap:6px}
  .sl-badge{display:none}
  .slider-row{grid-template-columns:1fr auto}
  .export-row{gap:6px}
  .btn-sm,.btn-secondary{font-size:9px;padding:6px 10px}
}
</style>
</head>
<body>

<!-- Ã¢â€¢ÂÃ¢â€¢Â REGISTRATION GATE Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â -->
<div class="reg-gate" id="reg-gate">
  <div class="reg-box">
    <div class="reg-box-hdr">
      <div class="reg-box-title">Think<span>LAB</span></div>
      <div class="reg-box-sub">Acceso Ã‚Â· Completa el registro para continuar</div>
    </div>
    <div class="reg-box-body">
      <!-- Spinner mientras carga el iframe -->
      <div class="reg-loading" id="reg-loading">
        <div class="reg-spin"></div>
        <div class="reg-load-txt">Cargando formulario...</div>
      </div>
      <!-- Pantalla de agradecimiento (post-envÃƒÂ­o) -->
      <div class="reg-thanks" id="reg-thanks">
        <div class="reg-check-circle">Ã¢Å“â€œ</div>
        <div class="reg-thanks-title">Ã‚Â¡Registro completado!</div>
        <div class="reg-thanks-sub">Gracias por registrarte. Ya tienes acceso completo a ThinkLab Ã¢â‚¬â€ la herramienta de anÃƒÂ¡lisis de marcas de Trademark Insights MÃƒÂ©xico.</div>
        <button class="reg-btn-enter" onclick="enterApp()">ENTRAR A LA APLICACIÃƒâ€œN Ã¢â€ â€™</button>
      </div>
      <!-- Google Form -->
      <iframe
        id="reg-iframe"
        class="reg-iframe"
        src="https://docs.google.com/forms/d/e/1FAIpQLSeOUP2x5mFLqdrjHOX6GEwbSXMMlZVxu7eqJtXqap5pVd0wQQ/viewform?embedded=true"
        frameborder="0"
        marginheight="0"
        marginwidth="0"
      >CargandoÃ¢â‚¬Â¦</iframe>
    </div>
  </div>
</div>

<div class="app-shell">

<!-- Ã¢â€â‚¬Ã¢â€â‚¬ Topbar Ã¢â€â‚¬Ã¢â€â‚¬ -->
<nav class="topbar">
  <a class="topbar-logo" href="#">
    <div class="wordmark">Facty</div>
    <div class="logo-divider"></div>
    <div class="by-block">
      <span class="tm-trademark">Trademark</span>
      <span class="tm-insights">Insights</span>
      <span class="tm-mexico">Mexico</span>
    </div>
  </a>
  <div class="topbar-spacer"></div>
  <button class="btn-nuevo" onclick="iniciarNuevo()">Ã¢â€ Âº NUEVO ANÃƒÂLISIS</button>
</nav>

<!-- Ã¢â€â‚¬Ã¢â€â‚¬ Auth Panel Ã¢â€â‚¬Ã¢â€â‚¬ -->
<div class="auth-panel hidden" id="auth-panel">
  <div class="auth-panel-title">
    <span id="auth-panel-label">Acceso a tu cuenta</span>
    <button class="auth-close" onclick="toggleAuthPanel()">Ã¢Å“â€¢</button>
  </div>

  <!-- Guest view -->
  <div id="auth-guest">
    <input class="auth-input" id="auth-email" type="email" placeholder="Correo electrÃƒÂ³nico" autocomplete="email"/>
    <input class="auth-input" id="auth-password" type="password" placeholder="ContraseÃƒÂ±a (mÃƒÂ­n. 6 caracteres)" autocomplete="current-password"/>
    <div class="auth-btns">
      <button class="btn-sm" onclick="loginUser()" style="flex:1">Entrar</button>
      <button class="btn-sm outline" onclick="registerUser()" style="flex:1">Registrarse</button>
    </div>
    <div class="auth-msg" id="auth-msg"></div>
  </div>

  <!-- Logged-in view -->
  <div id="auth-user" style="display:none">
    <div class="auth-user-info">
      <div class="auth-user-email" id="auth-user-email"></div>
      <div class="auth-user-role">Cuenta activa</div>
    </div>
    <button class="btn-danger-sm" onclick="logoutUser()" style="width:100%">Cerrar sesiÃƒÂ³n</button>
  </div>
</div>

<!-- Ã¢â€â‚¬Ã¢â€â‚¬ Main content Ã¢â€â‚¬Ã¢â€â‚¬ -->
<div class="main">

<!-- Ã¢â€â‚¬Ã¢â€â‚¬ Nota Legal Ã¢â€â‚¬Ã¢â€â‚¬ -->
<div class="nota-legal-wrap">
  <button class="nota-legal-toggle" onclick="toggleNotaLegal()">
    <span>Ã°Å¸â€œâ€ž NOTA LEGAL</span>
    <span class="nota-legal-chevron" id="nota-legal-chevron">Ã¢â€“Â¸</span>
  </button>
  <div class="nota-legal-body" id="nota-legal-body">
    <p>Al registrarte y usar Trademark Insights MÃƒÂ©xico (TIM) aceptas nuestros TÃƒÂ©rminos y Condiciones y Aviso de Privacidad.</p>
    <p>TIM es una herramienta gratuita de consulta indicativa. Sus resultados no constituyen asesorÃƒÂ­a legal ni garantizan la registrabilidad de un signo distintivo, y pueden cambiar en cualquier momento sin previo aviso.</p>
    <p>Como contraprestaciÃƒÂ³n al uso gratuito, autorizas la transferencia onerosa de tus datos personales y de la informaciÃƒÂ³n de tus consultas a terceros.</p>
    <p>Puedes ejercer tus derechos ARCO en cualquier momento escribiendo a <a href="mailto:consultas@werfurther.com">consultas@werfurther.com</a>.</p>
    <p>Ã°Å¸â€œâ€ž Consultar T&amp;C y Aviso de Privacidad completos en <a href="https://coda.io/d/_dz3m9xX6c8V/TRADEMARK-INSIGHTS-MEXICO_supg2Gm_" target="_blank" rel="noopener">https://coda.io/d/_dz3m9xX6c8V/TRADEMARK-INSIGHTS-MEXICO_supg2Gm_</a></p>
    <p>Responsable: CRRNZ Strategic Advisors, S.A.S. de C.V.</p>
  </div>
</div>

<!-- Ã¢â€¢ÂÃ¢â€¢Â WIZARD Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â -->

<!-- Step bar -->
<div class="wiz-bar" id="wiz-bar" style="margin-top:28px">
  <div class="wiz-fill" id="wiz-fill"></div>
  <div class="wiz-node">
    <div class="wiz-circle active" id="wc-1">1</div>
    <span class="wiz-label active" id="wl-1">Tu Marca</span>
  </div>
  <div class="wiz-node">
    <div class="wiz-circle" id="wc-2">2</div>
    <span class="wiz-label" id="wl-2">Giro de Negocio</span>
  </div>
  <div class="wiz-node">
    <div class="wiz-circle" id="wc-3">3</div>
    <span class="wiz-label" id="wl-3">Lanzar AnÃƒÂ¡lisis</span>
  </div>
</div>

<!-- Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ STEP 1 Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ -->
<div class="wiz-step active" id="ws-1">
  <div class="hero-grid">

    <!-- Left: form -->
    <div>
      <!-- Brand inputs -->
      <div class="card" style="margin-bottom:14px">
        <div class="card-title">Nueva BÃƒÂºsqueda <span id="fav-badge" style="font-weight:400;color:var(--muted)"></span></div>
        <div class="brand-list" id="brand-list">
          <div class="brand-row" data-idx="0">
            <span class="brand-num">1</span>
            <input type="text" class="brand-input" placeholder="Ej. QUANTUM TECH" autocomplete="off" spellcheck="false"/>
          </div>
        </div>
      </div>

      <!-- Analysis type selection -->
      <div class="card" style="margin-bottom:20px">
        <div class="card-title">Ã‚Â¿QuÃƒÂ© quieres verificar sobre tu marca?</div>
        <div class="analysis-types">
          <div class="at-card selected" id="at-marca" onclick="toggleAnalysis('marca')">
            <div class="at-icon">Ã¢Å¡â€“Ã¯Â¸Â</div>
            <div class="at-info">
              <div class="at-name">Ã‚Â¿Es Registrable?</div>
              <div class="at-desc">Conflictos IMPI Ã‚Â· ML</div>
            </div>
            <div class="at-check" id="ac-marca"></div>
          </div>
          <div class="at-card selected" id="at-social" onclick="toggleAnalysis('social')">
            <div class="at-icon">Ã°Å¸â€œÂ±</div>
            <div class="at-info">
              <div class="at-name">Ã‚Â¿Visible en Redes?</div>
              <div class="at-desc">25 plataformas</div>
            </div>
            <div class="at-check" id="ac-social"></div>
          </div>
          <div class="at-card selected" id="at-domain" onclick="toggleAnalysis('domain')">
            <div class="at-icon">Ã°Å¸Å’Â</div>
            <div class="at-info">
              <div class="at-name">Ã‚Â¿Encontrable en Web?</div>
              <div class="at-desc">18 extensiones de dominio</div>
            </div>
            <div class="at-check" id="ac-domain"></div>
          </div>
          <div class="at-card selected" id="at-mua" onclick="toggleAnalysis('mua')">
            <div class="at-icon">Ã°Å¸ÂÂ¢</div>
            <div class="at-info">
              <div class="at-name">Ã‚Â¿Disponible como Empresa?</div>
              <div class="at-desc">DenominaciÃƒÂ³n Social Ã‚Â· MUA</div>
            </div>
            <div class="at-check" id="ac-mua"></div>
          </div>
        </div>
      </div>

      <button class="btn-primary" onclick="wizNext(1)">CONTINUAR Ã¢â€ â€™</button>
    </div>

    <!-- Right: tagline -->
    <div class="hero-tagline">
      <div class="tagline-eyebrow">Brainlab Ã‚Â· Trademark Insights MÃƒÂ©xico</div>
      <div class="tagline-h1">
        Ã‚Â¿Tu nombre de<br>
        marca tiene<br>
        <em>futuro</em>?
      </div>
      <p class="tagline-body">
        Antes de invertir en tu negocio, descubre si tu marca puede <strong style="color:var(--text)">registrarse legalmente</strong>, si estÃƒÂ¡ disponible en redes sociales, si puedes tener tu propio dominio web y si ya existe como empresa en MÃƒÂ©xico.
      </p>
      <ul class="tagline-checklist">
        <li>VerificaciÃƒÂ³n de conflictos en el IMPI (Instituto Mexicano de la Propiedad Industrial)</li>
        <li>Disponibilidad en Instagram, TikTok, X, LinkedIn y 21 plataformas mÃƒÂ¡s</li>
        <li>Disponibilidad de dominios .com, .mx, .io y 15 extensiones mÃƒÂ¡s</li>
        <li>Consulta de denominaciones sociales en el Registro PÃƒÂºblico MUA</li>
      </ul>
    </div>
  </div>
</div>

<!-- Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ STEP 2: Giro de Negocio Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ -->
<div class="wiz-step" id="ws-2">
  <button class="btn-back" onclick="wizBack(2)">Ã¢â€ Â Regresar</button>

  <!-- Selected giro banner -->
  <div class="giro-selected-banner" id="giro-banner">
    <div class="gsb-cls" id="gsb-cls-num">Ã¢â‚¬â€</div>
    <div class="gsb-info">
      <div class="gsb-cat" id="gsb-cat-name">Ã¢â‚¬â€</div>
      <div class="gsb-note" id="gsb-cat-desc">Clase Niza asignada automÃƒÂ¡ticamente</div>
    </div>
    <button class="gsb-clear" onclick="clearGiro()" title="Cambiar giro">Ã¢Å“â€¢</button>
  </div>

  <div class="card">
    <div class="card-title" style="margin-bottom:12px">Ã‚Â¿A quÃƒÂ© se dedica tu negocio o marca?</div>
    <p style="font-size:12px;color:var(--muted);margin-bottom:16px;line-height:1.6">
      Selecciona la categorÃƒÂ­a que mejor describe tu negocio. Asignaremos automÃƒÂ¡ticamente la <strong style="color:var(--text)">Clase Niza</strong> correspondiente para el anÃƒÂ¡lisis de marcas en conflicto ante el IMPI.
    </p>

    <!-- Filter pills -->
    <div class="giro-filter-pills">
      <button class="gfp active" id="gfp-all" onclick="setGiroFilter('all')">Todos los giros</button>
      <button class="gfp" id="gfp-prod" onclick="setGiroFilter('producto')">Productos</button>
      <button class="gfp" id="gfp-serv" onclick="setGiroFilter('servicio')">Servicios</button>
    </div>

    <!-- Search -->
    <div class="giro-search-wrap">
      <span class="giro-search-icon">Ã°Å¸â€Â</span>
      <input type="text" class="giro-search" id="giro-search" placeholder="Busca tu giro: restaurante, software, ropa, consultorÃƒÂ­a..." oninput="filterGiros()"/>
    </div>

    <!-- Grid of giros -->
    <div class="giro-grid" id="giro-grid"></div>
  </div>

  <button class="btn-primary" onclick="wizNext(2)" id="btn-continuar-2">CONTINUAR Ã¢â€ â€™</button>
</div>

<!-- Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ STEP 3: Lanzar Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ -->
<div class="wiz-step" id="ws-3">
  <button class="btn-back" onclick="wizBack(3)">Ã¢â€ Â Regresar</button>
  <button class="btn-primary" id="run-btn" onclick="startAnalysis()" style="margin-top:16px">Ã¢â€“Â¶ INICIAR ANÃƒÂLISIS</button>
</div>

<!-- Ã¢â€¢ÂÃ¢â€¢Â RESULTS Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â -->
<div id="results-area" style="margin-top:28px">
  <div id="brand-tabs-wrap" style="display:none">
    <div class="brand-tabs-bar" id="btabs-bar"></div>
  </div>
  <div id="btabs-contents"></div>
</div>

<!-- Ã¢â€â‚¬Ã¢â€â‚¬ Compare area Ã¢â€â‚¬Ã¢â€â‚¬ -->
<div id="compare-area" style="display:none;margin-top:8px"></div>

<!-- Ã¢â€â‚¬Ã¢â€â‚¬ MODALS Ã¢â€â‚¬Ã¢â€â‚¬ -->
<!-- Ver Todos -->
<div class="modal-back" id="vt-back" onclick="closeVtModal(event)">
  <div class="modal-box">
    <button class="modal-close" onclick="document.getElementById('vt-back').classList.remove('show')">Ã¢Å“â€¢</button>
    <div class="modal-title" id="vt-title">Todas las Clases Niza</div>
    <div class="modal-sub" id="vt-sub"></div>
    <div class="vt-grid" id="vt-grid"></div>
  </div>
</div>
<!-- Criteria info -->
<div class="modal-back" id="crit-back" onclick="closeCritModal(event)">
  <div class="modal-box">
    <button class="modal-close" onclick="document.getElementById('crit-back').classList.remove('show')">Ã¢Å“â€¢</button>
    <div class="modal-title">Criterios de AnÃƒÂ¡lisis</div>
    <div class="modal-sub">Sistema de evaluaciÃƒÂ³n de riesgo de no-concesiÃƒÂ³n</div>
    <div class="crit-grid">
      <div class="crit-card"><div class="crit-num">C1</div><div class="crit-name">Distancia Levenshtein</div><div class="crit-val" id="mc1">Ã¢â€°Â¤ 30%</div><div class="crit-desc">Similitud ortogrÃƒÂ¡fica. Valores bajos = alta similitud visual.</div></div>
      <div class="crit-card"><div class="crit-num">C2</div><div class="crit-name">Similitud Jaro-Winkler</div><div class="crit-val" id="mc2">Ã¢â€°Â¥ 87%</div><div class="crit-desc">Similitud fonÃƒÂ©tica. Alta similitud = riesgo de confusiÃƒÂ³n auditiva.</div></div>
      <div class="crit-card"><div class="crit-num">C3</div><div class="crit-name">Prob. ConfusiÃƒÂ³n (ML)</div><div class="crit-val" id="mc3">Ã¢â€°Â¥ 50%</div><div class="crit-desc">Probabilidad de que el pÃƒÂºblico confunda las marcas.</div></div>
      <div class="crit-card"><div class="crit-num">C4</div><div class="crit-name">Prob. ConcesiÃƒÂ³n (ML)</div><div class="crit-val" id="mc4">Ã¢â€°Â¤ 89%</div><div class="crit-desc">Probabilidad baja de concesiÃƒÂ³n = riesgo de rechazo.</div></div>
    </div>
    <div class="concesion-rule">Se otorga <strong style="color:var(--green)">CONCESIÃƒâ€œN</strong> cuando <span class="rule-hl" id="mc-rule">Ã¢â€°Â¤ 1 criterio activo</span>. Con <span id="mc-min">2</span> o mÃƒÂ¡s criterios Ã¢â€ â€™ <strong style="color:var(--red)">NO CONCESIÃƒâ€œN</strong>.</div>
  </div>
</div>

<div class="toast" id="toast"></div>
</div><!-- /main -->
</div><!-- /app-shell -->

<script>
'use strict';
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// STATE
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
let currentStep = 1;
let selectedMode = 'T';
let selectedClases = [];
let perBrandMode = false;
let brandClases = {};
let brandModes = {};
let brandList = [''];
let brandResults = {};
let socialResultsData = {};
let domainResultsData = {};
let muaResultsData = {};
let activeBrandIdx = 0;
let favorites = JSON.parse(localStorage.getItem('tim_fav') || '[]');
let selectedAnalysis = {marca:true, social:true, domain:true, mua:true};
let selectedGiro = null; // {cls, category, description, type}
let sigaResults = {}; // brandIdx Ã¢â€ â€™ siga result data
const CRITERIA_DEFAULT = {dist:30, sim:87, conf:50, conc:89, minCount:2};
let criteriaConfig = {...CRITERIA_DEFAULT};
let criteriaMode = 'default';
const chartInstances = {};
const chartCenterText = {};
let _tickerIdxByBrand = {};
let _activeTickerByBrand = {};
let _classDataByBrand = {};
let _toastTimer = null;

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// WIZARD
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function wizGo(step){
  const prev = document.getElementById('ws-'+currentStep);
  const next = document.getElementById('ws-'+step);
  if(!prev||!next) return;
  prev.classList.remove('active');
  // Small delay for animation
  setTimeout(()=>{
    next.classList.add('active');
    document.getElementById('wiz-bar').scrollIntoView({behavior:'smooth',block:'nearest'});
  },50);
  currentStep = step;
  updateWizBar(step);
}

function wizNext(from){
  if(from===1){
    syncBrandList();
    if(!brandList.filter(b=>b.trim()).length){ showToast('Ingresa al menos una marca'); return; }
    if(!Object.values(selectedAnalysis).some(v=>v)){ showToast('Selecciona al menos un tipo de anÃƒÂ¡lisis'); return; }
    if(selectedAnalysis.marca) wizGo(2); else wizGo(3);
  } else if(from===2){
    if(selectedAnalysis.marca && !selectedGiro){ showToast('Selecciona el giro de tu negocio'); return; }
    wizGo(3);
  }
}
function wizBack(from){
  if(from===3 && !selectedAnalysis.marca) wizGo(1);
  else wizGo(from-1);
}

function updateWizBar(active){
  [1,2,3].forEach(n=>{
    const c=document.getElementById('wc-'+n), l=document.getElementById('wl-'+n);
    c.className='wiz-circle';l.className='wiz-label';
    if(n<active){c.classList.add('done');c.textContent='Ã¢Å“â€œ';l.classList.add('done');}
    else if(n===active){c.classList.add('active');c.textContent=String(n);l.classList.add('active');}
    else{c.textContent=String(n);}
  });
  const fill=document.getElementById('wiz-fill');
  const bar=document.getElementById('wiz-bar');
  const tw=bar.offsetWidth-28-28-32;
  if(active===1) fill.style.width='0';
  else if(active===2) fill.style.width=(tw/2)+'px';
  else fill.style.width=tw+'px';
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// GIRO DE NEGOCIO
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
const NIZA_DATA = [
  {n:1,type:"producto",h:"QuÃƒÂ­mica e industria",i:["Fertilizantes y abonos","Productos quÃƒÂ­micos industriales","Adhesivos industriales","Resinas artificiales","Solventes y diluyentes","Colorantes industriales","Compost orgÃƒÂ¡nico","Herbicidas","Insecticidas","Fungicidas","AgroquÃƒÂ­micos","Productos para curtido de cuero","Preparaciones biolÃƒÂ³gicas","Aceites esenciales para industria","Enzimas industriales","Productos para tratamiento de agua","Compuestos para soldadura","Materias plÃƒÂ¡sticas en bruto","Productos quÃƒÂ­micos para fotografÃƒÂ­a","Productos para extinciÃƒÂ³n de incendios","ÃƒÂcidos industriales","Catalizadores","Inhibidores de corrosiÃƒÂ³n"]},
  {n:2,type:"producto",h:"Pinturas y revestimientos",i:["Pinturas decorativas","Barnices","Lacas","Esmaltes","Pintura automotriz","Pintura para paredes","Pintura en spray","Antioxidantes y anticorrosivos","Colorantes","Tintes para cabello","Tintas de impresiÃƒÂ³n","Pigmentos","Recubrimientos metÃƒÂ¡licos","Imprimantes y selladores","Pintura epÃƒÂ³xica","Pintura para madera","Barniz para pisos"]},
  {n:3,type:"producto",h:"CosmÃƒÂ©ticos y limpieza",i:["Shampoo","Perfumes y fragancias","Cremas hidratantes","Maquillaje","CosmÃƒÂ©ticos","JabÃƒÂ³n","Detergente","Desodorante","Protector solar","Bloqueador solar","Pasta dental","Acondicionador","Crema facial","Crema corporal","Gel de ducha","Esmalte de uÃƒÂ±as","Lociones","Colonias","Productos para blanquear ropa","Limpiadores domÃƒÂ©sticos","Cera para pisos","Quitamanchas","Desengrasante domÃƒÂ©stico","Gel para cabello","TÃƒÂ³nico capilar","Crema antienvejecimiento","SÃƒÂ©rum facial","Mascarilla facial","BÃƒÂ¡lsamo labial","Crema para manos","Limpieza facial","Desmaquillante","TÃƒÂ³nico facial","Aromatizante de ambiente"]},
  {n:4,type:"producto",h:"Aceites, combustibles y lubricantes",i:["Aceite lubricante","Aceite de motor","Lubricantes industriales","Gasolina","Combustibles","Ceras industriales","Grasa mecÃƒÂ¡nica","Velas de iluminaciÃƒÂ³n","Aceite para maquinaria","PetrÃƒÂ³leo","Productos petroquÃƒÂ­micos","Aceite hidrÃƒÂ¡ulico","Anticongelantes","BujÃƒÂ­as de iluminaciÃƒÂ³n"]},
  {n:5,type:"producto",h:"FarmacÃƒÂ©uticos y sanitarios",i:["Medicamentos","Productos farmacÃƒÂ©uticos","Vitaminas","Suplementos alimenticios","AntibiÃƒÂ³ticos","AnalgÃƒÂ©sicos","Antiinflamatorios","Vacunas","Productos veterinarios","Desinfectantes","Mascarillas sanitarias","Vendas y apÃƒÂ³sitos","ProbiÃƒÂ³ticos","ProteÃƒÂ­nas y suplementos deportivos","Productos homeopÃƒÂ¡ticos","Preparaciones herbales","Material para curaciÃƒÂ³n","Anticonceptivos","Cremas medicinales","AntihistamÃƒÂ­nicos","Cannabis medicinal","ColÃƒÂ¡geno","Alimentos para bebÃƒÂ©s","Dietas mÃƒÂ©dicas","Productos sanitarios femeninos"]},
  {n:6,type:"producto",h:"Metales comunes",i:["Estructuras metÃƒÂ¡licas","HerrerÃƒÂ­a","Cables metÃƒÂ¡licos","Cerraduras","Candados","Bisagras","Tornillos y clavos","Materiales de construcciÃƒÂ³n metÃƒÂ¡licos","Contenedores metÃƒÂ¡licos","FerreterÃƒÂ­a","Marcos de metal","Rejas metÃƒÂ¡licas","Puertas metÃƒÂ¡licas","Cajas fuertes","TuberÃƒÂ­as metÃƒÂ¡licas","Grapas y sujetadores","Placas y lÃƒÂ¡minas de metal","Perfiles metÃƒÂ¡licos","Alcantarillas metÃƒÂ¡licas"]},
  {n:7,type:"producto",h:"Maquinaria e industria",i:["MÃƒÂ¡quinas industriales","Motores industriales","Herramientas mecÃƒÂ¡nicas","Maquinaria agrÃƒÂ­cola","Bombas industriales","Compresores","Generadores elÃƒÂ©ctricos","Robots industriales","Prensas industriales","MÃƒÂ¡quinas de coser industriales","Impresoras 3D","AutomatizaciÃƒÂ³n industrial","Equipos CNC","Maquinaria de construcciÃƒÂ³n","Excavadoras","GrÃƒÂºas","Tractores","Tornos y fresadoras","MÃƒÂ¡quinas empacadoras","Equipos de refrigeraciÃƒÂ³n industrial","Ventiladores industriales","Maquinaria de alimentos"]},
  {n:8,type:"producto",h:"Herramientas manuales",i:["Herramientas de mano","Cuchillos","Tenedores y cucharas","Tijeras","Destornilladores","Martillos","Llaves de tuercas","Pinzas","Navajas","CuchillerÃƒÂ­a de cocina","Herramientas para jardÃƒÂ­n","Sacacorchos","Podadoras manuales","Abrelatas","Cortadores","EspÃƒÂ¡tulas de mano","Maquinillas de afeitar"]},
  {n:9,type:"producto",h:"ElectrÃƒÂ³nica y software",i:["Software","Aplicaciones mÃƒÂ³viles","Apps","Hardware","Computadoras","Laptops","Smartphones","Tablets","CÃƒÂ¡maras fotogrÃƒÂ¡ficas","CÃƒÂ¡maras de seguridad","VideocÃƒÂ¡maras","Televisores","Bocinas y altavoces","Auriculares y headphones","Sensores electrÃƒÂ³nicos","GPS","Drones","Realidad virtual y aumentada","Inteligencia artificial","Videojuegos","Consolas de videojuegos","BaterÃƒÂ­as y cargadores","Memorias USB","Discos duros","Servidores","Antivirus","Plataformas digitales","E-commerce","SaaS","Cloud computing","Relojes inteligentes","Smartwatches","Robots domÃƒÂ©sticos","CÃƒÂ¡maras de acciÃƒÂ³n","Paneles solares","Impresoras","EscÃƒÂ¡neres","Equipos de seguridad electrÃƒÂ³nica","Rastreadores GPS","Bases de datos","Machine learning"]},
  {n:10,type:"producto",h:"Instrumentos mÃƒÂ©dicos",i:["Equipos mÃƒÂ©dicos","Aparatos mÃƒÂ©dicos","Dispositivos mÃƒÂ©dicos","Sillas de ruedas","PrÃƒÂ³tesis y ÃƒÂ³rtesis","Lentes de contacto","Gafas y anteojos mÃƒÂ©dicos","Aparatos dentales","Equipos de diagnÃƒÂ³stico","Instrumental quirÃƒÂºrgico","Jeringas y agujas","Equipos ortopÃƒÂ©dicos","ArtÃƒÂ­culos para bebÃƒÂ©","Monitores de presiÃƒÂ³n arterial","GlucÃƒÂ³metros","TermÃƒÂ³metros mÃƒÂ©dicos","Equipos de fisioterapia","Camas hospitalarias","Andaderas y muletas","AudÃƒÂ­fonos para sordera","Equipos de ultrasonido"]},
  {n:11,type:"producto",h:"IluminaciÃƒÂ³n y sanitarios",i:["LÃƒÂ¡mparas","Luminarias LED","Focos LED","Ventiladores de techo","Aires acondicionados","Calentadores","Estufas","Hornos","Lavaplatos","Refrigeradores","Sanitarios y retretes","Lavabos","Regaderas","Purificadores de agua","Extractores de cocina","Tinacos y boilers","Calefactores","VentilaciÃƒÂ³n industrial","Filtros de agua","Jacuzzi","Secadores de ropa","ClimatizaciÃƒÂ³n"]},
  {n:12,type:"producto",h:"VehÃƒÂ­culos y transporte",i:["AutomÃƒÂ³viles","Coches","Motocicletas","Bicicletas","Camiones","Autobuses","Barcos","Aviones","Scooters elÃƒÂ©ctricos","Patinetas elÃƒÂ©ctricas","VehÃƒÂ­culos elÃƒÂ©ctricos","Partes de automÃƒÂ³vil","Llantas y neumÃƒÂ¡ticos","Remolques","Cuatrimotos","CarrocerÃƒÂ­as","Drones aÃƒÂ©reos","Embarcaciones"]},
  {n:13,type:"producto",h:"Armas y explosivos",i:["Armas de fuego","Pistolas","Rifles","Municiones","Cartuchos","Explosivos","Pirotecnia","Fuegos artificiales","Bengalas","Armas de defensa personal"]},
  {n:14,type:"producto",h:"JoyerÃƒÂ­a y relojerÃƒÂ­a",i:["JoyerÃƒÂ­a","Joyas","Relojes","Anillos","Collares","Pulseras","Aretes y pendientes","Broches","Medallas","Trofeos","BisuterrÃƒÂ­a fina","JoyerÃƒÂ­a de oro y plata","Diamantes","Piedras preciosas","Plata esterlina","JoyerÃƒÂ­a artesanal","Relojes de lujo","Relojes inteligentes (joyerÃƒÂ­a)"]},
  {n:15,type:"producto",h:"Instrumentos musicales",i:["Guitarras","Piano y teclados","ViolÃƒÂ­n","BaterÃƒÂ­a","Instrumentos musicales","MicrÃƒÂ³fonos","Amplificadores","Cuerdas musicales","Trompetas","Saxofones","Flautas","Percusiones","Bajos elÃƒÂ©ctricos","Ukuleles","Acordeones","Boquillas","Atriles"]},
  {n:16,type:"producto",h:"PapelerÃƒÂ­a e imprenta",i:["PapelerÃƒÂ­a","Libros","Revistas","Cuadernos","BolÃƒÂ­grafos y plumas","LÃƒÂ¡pices","Carpetas y archiveros","Material didÃƒÂ¡ctico","Tarjetas de presentaciÃƒÂ³n","Material de oficina","Sellos y stickers","Etiquetas","Mapas","Calendarios","Material de impresiÃƒÂ³n","Publicaciones","PeriÃƒÂ³dicos","Material escolar","Agendas","Manualidades","Pintura para niÃƒÂ±os","Libros de texto","Arte y dibujo","Papel fotogrÃƒÂ¡fico"]},
  {n:17,type:"producto",h:"Caucho y materiales aislantes",i:["Caucho","Goma","PlÃƒÂ¡sticos industriales semielaborados","TuberÃƒÂ­as flexibles","Mangueras","Materiales de aislamiento","Hule","Silicona industrial","Sellos y empaques industriales","Materiales para calafatear","Fibra de vidrio","Espuma de poliuretano"]},
  {n:18,type:"producto",h:"Cuero y equipaje",i:["Bolsas de mano","Mochilas","Maletas y equipaje","Carteras","Billeteras","Monederos","Cinturones","Cuero y piel","Paraguas","Sombrillas","Portafolios","Bolsos de diseÃƒÂ±ador","Bolsos de playa","RiÃƒÂ±oneras","Correas para mascotas","Collares para mascotas","PortabebÃƒÂ©s","Bolsas de cuero artesanal"]},
  {n:19,type:"producto",h:"Materiales de construcciÃƒÂ³n",i:["Materiales de construcciÃƒÂ³n","Cemento","Ladrillos y tabiques","Azulejos","Tejas","Yeso","Concreto","Madera para construcciÃƒÂ³n","Pisos","Puertas","Ventanas","MÃƒÂ¡rmol","Granito","Asfalto","Impermeabilizante","Block y tabicÃƒÂ³n","Arena y grava","Paneles de construcciÃƒÂ³n","Drywall","Muros prefabricados","Losas","Recubrimientos no metÃƒÂ¡licos"]},
  {n:20,type:"producto",h:"Muebles y contenedores",i:["Muebles","Sillas","Mesas","Camas","SofÃƒÂ¡s y sillones","Escritorios","Libreros","Closets","Gabinetes","Espejos","Marcos y cuadros","Cajas de almacenamiento","Canastas","Hamacas","Sillas de oficina","Cocinas integrales","Colchones","Muebles de jardÃƒÂ­n","EstanterÃƒÂ­as","Puff y otomanas","Muebles para baÃƒÂ±o"]},
  {n:21,type:"producto",h:"Utensilios domÃƒÂ©sticos",i:["Utensilios de cocina","Ollas y cazuelas","Sartenes","Platos","Vasos y copas","Tazas","Moldes para horno","Recipientes y contenedores","BaterÃƒÂ­as de cocina","Cepillos de dientes","Esponjas","Porcelana y cerÃƒÂ¡mica","CristalerÃƒÂ­a","Jarras y termos","Cucharones y espÃƒÂ¡tulas","Peladores y ralladores","Coladores","Tablas para picar","Freidoras de aire"]},
  {n:22,type:"producto",h:"Cuerdas, redes y materiales",i:["Cuerdas y sogas","Redes","Tiendas de campaÃƒÂ±a","Carpas","Lonas y toldos","Sacos industriales","Redes de pesca","Redes deportivas","Cuerdas de escalada","Materiales de embalaje textil"]},
  {n:23,type:"producto",h:"Hilos e hilados",i:["Hilos para coser","Hilados textiles","Lana","Hilo de bordar","Hilo para crochet","Hilo para tejer","Fibras textiles en bruto","Hilo industrial","Hilo de algodÃƒÂ³n","Hilo de poliÃƒÂ©ster"]},
  {n:24,type:"producto",h:"Tejidos y ropa de hogar",i:["SÃƒÂ¡banas","Cobijas y cobertores","Manteles","Cortinas","Toallas","Telas y tejidos","Ropa de cama","Fundas","Colchas","Tapetes de tela","Almohadas","MantelerÃƒÂ­a","Tapices","Telas para tapizar"]},
  {n:25,type:"producto",h:"Ropa y calzado",i:["Ropa","Playeras y camisetas","Camisas","Pantalones","Faldas","Vestidos","Zapatos","Tenis y sneakers","Botas","Sandalias","Calcetines","Ropa interior","Uniformes","Calzado deportivo","Sombreros y gorras","Ropa deportiva","Trajes y sacos","Jeans","Chaquetas y abrigos","Ropa para bebÃƒÂ©","Pijamas","Trajes de baÃƒÂ±o","Leggings","Sudaderas","Chamarras","Ropa de trabajo","Pantuflas","Trajes de novia","Disfraces"]},
  {n:26,type:"producto",h:"MercerÃƒÂ­a y accesorios textiles",i:["Botones","Cierres y cremalleras","Agujas y alfileres","Bordados","Listones y cintas","Encajes","Flores artificiales","Accesorios para el cabello","Diademas","Broches para ropa","Velcro","ElÃƒÂ¡sticos","Parches bordados","Adornos para ropa"]},
  {n:27,type:"producto",h:"Alfombras y revestimientos de suelo",i:["Alfombras","Tapetes","Pisos laminados","Revestimientos de suelo","Pisos de vinilo","Tapetes decorativos","Pisos de madera","Tapetes de baÃƒÂ±o","Tapetes de cocina","Pisos de hule","Tapetes antiderrapantes"]},
  {n:28,type:"producto",h:"Juegos, juguetes y deporte",i:["Juguetes","Juegos de mesa","Videojuegos","ArtÃƒÂ­culos deportivos","Balones y pelotas","Bicicletas de ejercicio","Pesas y mancuernas","Equipos de gimnasio","Raquetas","Patines","Patinetas","Equipo de nataciÃƒÂ³n","Material de bÃƒÂ©isbol","Material de fÃƒÂºtbol","Material de bÃƒÂ¡squetbol","Adornos navideÃƒÂ±os","MuÃƒÂ±ecas","Figuras de acciÃƒÂ³n","Rompecabezas","Equipo de camping","Dardos","Mesa de ping pong","Cuerdas para saltar","Inflables","Equipos de yoga"]},
  {n:29,type:"producto",h:"Alimentos cÃƒÂ¡rnicos y lÃƒÂ¡cteos",i:["Carne de res","Carne de pollo","Carne de cerdo","Pescado y mariscos","Leche","Queso","Yogur","Mantequilla","Crema","Embutidos","JamÃƒÂ³n","Salchicha","Frutas en conserva","Verduras en conserva","Aceite de oliva","Aceite vegetal","Manteca","Huevos","AtÃƒÂºn enlatado","Sardinas","Caldos enlatados","Leche evaporada","Crema ÃƒÂ¡cida","Queso panela","Queso Oaxaca","ProteÃƒÂ­na animal"]},
  {n:30,type:"producto",h:"Cereales, panaderÃƒÂ­a y condimentos",i:["CafÃƒÂ©","CafÃƒÂ© de especialidad","CafÃƒÂ© molido","CafÃƒÂ© en cÃƒÂ¡psulas","CafÃƒÂ© orgÃƒÂ¡nico","TÃƒÂ©","Cacao","Chocolate","Pan","Pasteles y pastelerÃƒÂ­a","Galletas","Tortillas","Arroz","Pasta y fideos","Harina","AzÃƒÂºcar","Sal","Especias y condimentos","Salsas","Mermeladas","Miel","Helado","Paletas","Dulces y confiterÃƒÂ­a","Cereales para desayuno","Chocolates artesanales","Postres","PanaderÃƒÂ­a artesanal","Snacks","Botanas","Granola"]},
  {n:31,type:"producto",h:"Productos agrÃƒÂ­colas y animales",i:["Frutas frescas","Verduras frescas","Hortalizas","Plantas de ornato","Flores naturales","Semillas para siembra","Animales vivos","Alimentos para mascotas","Comida para perros","Comida para gatos","Granos sin procesar","MaÃƒÂ­z","Frijol","CafÃƒÂ© en grano","Aguacate","Hierbas aromÃƒÂ¡ticas frescas","Cactus","Plantas medicinales","Hongos comestibles"]},
  {n:32,type:"producto",h:"Cervezas y bebidas sin alcohol",i:["Agua embotellada","Agua purificada","Agua mineralizada","Refrescos","Bebidas energÃƒÂ©ticas","Jugos y nÃƒÂ©ctares","Bebidas deportivas","Aguas frescas","TÃƒÂ© frÃƒÂ­o","Limonada","Cerveza sin alcohol","Kombucha","Bebidas naturales","Bebidas funcionales","Tepache","Agua de coco","Bebidas de proteÃƒÂ­nas","Bebidas fermentadas sin alcohol","Cervezas artesanales"]},
  {n:33,type:"producto",h:"Bebidas alcohÃƒÂ³licas",i:["Vino","Tequila","Mezcal","Whisky","Ron","Vodka","Brandy","Licores","Aguardiente","Pulque","Sotol","Raicilla","Destilados artesanales","Cerveza (alcohÃƒÂ³lica)","Sidra","Gin","Sake","Bebidas alcohÃƒÂ³licas de sabores","Amaretto","Champagne"]},
  {n:34,type:"producto",h:"Tabaco y artÃƒÂ­culos para fumadores",i:["Cigarros","Tabaco","Puros","Cigarrillos electrÃƒÂ³nicos","Vapeadores","Vaporizadores","Nicotina","Encendedores","Pipa para tabaco","Tabaco de pipa","Hookah","Shisha","Tabaco sin humo"]},
  {n:35,type:"servicio",h:"Publicidad y administraciÃƒÂ³n de negocios",i:["Publicidad","Marketing","Marketing digital","GestiÃƒÂ³n de redes sociales","Agencia de publicidad","ConsultorÃƒÂ­a de negocios","AdministraciÃƒÂ³n empresarial","Recursos humanos","Contabilidad","Servicios de oficina","Branding","Relaciones pÃƒÂºblicas","SEO y SEM","Social media management","Influencer marketing","GestiÃƒÂ³n de marca","Franquicias","Outsourcing","Call center","Telemarketing","Agencia de mercadotecnia","RepresentaciÃƒÂ³n comercial","GestiÃƒÂ³n de e-commerce","AnÃƒÂ¡lisis de mercado","ConsultorÃƒÂ­a de ventas","SelecciÃƒÂ³n de personal","Headhunting","ProducciÃƒÂ³n de contenido","CRM y gestiÃƒÂ³n de clientes","GestiÃƒÂ³n de eventos empresariales","NÃƒÂ³mina y IMSS"]},
  {n:36,type:"servicio",h:"Finanzas, seguros e inmobiliaria",i:["Servicios financieros","Banca","CrÃƒÂ©ditos y prÃƒÂ©stamos","Seguros de vida","Seguros de automÃƒÂ³vil","Seguros mÃƒÂ©dicos","Seguros empresariales","Fintech","Inversiones","Bolsa de valores","Bienes raÃƒÂ­ces","Inmobiliaria","Compraventa de propiedades","AdministraciÃƒÂ³n de propiedades","Arrendamiento","Hipotecas","Cambio de divisas","Criptomonedas","Pagos electrÃƒÂ³nicos","Procesamiento de pagos","ValuaciÃƒÂ³n de inmuebles","AdministraciÃƒÂ³n de patrimonio","Fondos de inversiÃƒÂ³n","Microfinanzas","Crowdfunding"]},
  {n:37,type:"servicio",h:"ConstrucciÃƒÂ³n y reparaciÃƒÂ³n",i:["ConstrucciÃƒÂ³n","ReparaciÃƒÂ³n","Mantenimiento","PlomerÃƒÂ­a","Electricista","AlbaÃƒÂ±ilerÃƒÂ­a","Pintura de edificios","RemodelaciÃƒÂ³n","RenovaciÃƒÂ³n","InstalaciÃƒÂ³n de aire acondicionado","InstalaciÃƒÂ³n elÃƒÂ©ctrica","Limpieza industrial","Lavado de autos","Taller mecÃƒÂ¡nico","ReparaciÃƒÂ³n de electrÃƒÂ³nicos","MinerÃƒÂ­a","PerforaciÃƒÂ³n","CarpinterÃƒÂ­a","HerrerÃƒÂ­a","ImpermeabilizaciÃƒÂ³n","InstalaciÃƒÂ³n de paneles solares","JardinerÃƒÂ­a","FumigaciÃƒÂ³n","Control de plagas","Mantenimiento de albercas","RefrigeraciÃƒÂ³n y aire"]},
  {n:38,type:"servicio",h:"Telecomunicaciones",i:["Telecomunicaciones","Internet","TelefonÃƒÂ­a","Comunicaciones digitales","Streaming","TransmisiÃƒÂ³n en vivo","MensajerÃƒÂ­a instantÃƒÂ¡nea","Correo electrÃƒÂ³nico (servicio)","Redes de comunicaciÃƒÂ³n","TelevisiÃƒÂ³n por cable","TelevisiÃƒÂ³n satelital","Radio","Podcasts","Comunicaciones satelitales","VoIP","Servicio de datos mÃƒÂ³viles","Redes 5G","Hosting de contenido","Videoconferencias","RadiodifusiÃƒÂ³n"]},
  {n:39,type:"servicio",h:"Transporte y logÃƒÂ­stica",i:["Transporte","LogÃƒÂ­stica","MensajerÃƒÂ­a","PaqueterÃƒÂ­a","Delivery","EnvÃƒÂ­os","Mudanzas","Almacenamiento","Agencia de viajes","Tours y turismo","Carga y flete","Courrier","Servicio de taxi","Transporte en app","Renta de vehÃƒÂ­culos","Transporte de pasajeros","DistribuciÃƒÂ³n","Transporte aÃƒÂ©reo","Carga internacional","Aduanas (agente)","ÃƒÅ¡ltima milla","Cadena de suministro","AlmacÃƒÂ©n frigorÃƒÂ­fico"]},
  {n:40,type:"servicio",h:"Tratamiento de materiales",i:["ImpresiÃƒÂ³n","Imprenta","SerigrafÃƒÂ­a","Bordado","Reciclaje","Tratamiento de agua","PurificaciÃƒÂ³n","ConservaciÃƒÂ³n de alimentos","Procesamiento de materiales","Manufactura por encargo","Corte y ensamblaje","Galvanizado","Tratamiento de madera","SublimaciÃƒÂ³n","Grabado","Pintura industrial","Moldeado","Procesamiento de alimentos","ClasificaciÃƒÂ³n y envasado"]},
  {n:41,type:"servicio",h:"EducaciÃƒÂ³n, entretenimiento y deporte",i:["EducaciÃƒÂ³n","Escuela y colegio","Universidad","Cursos y talleres","CapacitaciÃƒÂ³n y entrenamiento","Coaching","TutorÃƒÂ­as","Clases en lÃƒÂ­nea","E-learning","Plataformas educativas","Entretenimiento","Teatro","Conciertos y eventos","ProducciÃƒÂ³n de contenido","FotografÃƒÂ­a","VideografÃƒÂ­a","Cine y producciÃƒÂ³n audiovisual","Publicaciones y ediciÃƒÂ³n","Deportes","Clubes deportivos","Actividades culturales","ProducciÃƒÂ³n musical","Estudio de grabaciÃƒÂ³n","Streaming de entretenimiento","Gaming en lÃƒÂ­nea","Parques de diversiÃƒÂ³n","Biblioteca y museos","Clases de idiomas","Yoga y meditaciÃƒÂ³n","Fitness y gimnasio"]},
  {n:42,type:"servicio",h:"Servicios cientÃƒÂ­ficos y tecnolÃƒÂ³gicos",i:["Desarrollo de software","ProgramaciÃƒÂ³n","Desarrollo web","Desarrollo de apps","DiseÃƒÂ±o web","UX/UI design","ConsultorÃƒÂ­a tecnolÃƒÂ³gica","Cloud computing","Ciberseguridad","Inteligencia artificial","Machine learning","AnÃƒÂ¡lisis de datos","Big data","Blockchain","Hosting y alojamiento web","Soporte tÃƒÂ©cnico IT","InvestigaciÃƒÂ³n y desarrollo","DiseÃƒÂ±o grÃƒÂ¡fico","DiseÃƒÂ±o industrial","Testing y QA","DevOps","SaaS","Ciencia de datos","IoT","Realidad virtual","GeolocalizaciÃƒÂ³n","Control de calidad","IngenierÃƒÂ­a de software","AuditorÃƒÂ­a tecnolÃƒÂ³gica","ConsultorÃƒÂ­a de IA"]},
  {n:43,type:"servicio",h:"RestauraciÃƒÂ³n y hospedaje",i:["Restaurante","CafÃƒÂ© y cafeterÃƒÂ­a","Bar","Cantina","Comida rÃƒÂ¡pida","Fast food","PanaderÃƒÂ­a y pastelerÃƒÂ­a","Catering","Servicio de banquetes","Hotel","Hostal","Hospedaje","Motel","Posada","Glamping","Comida a domicilio","Delivery de comida","Food truck","Cocina de autor","Cocina gourmet","Brunch","Sushi","TaquerÃƒÂ­a","PizzerÃƒÂ­a","Hamburguesas","Comida vegana","Comida saludable","Buffet","Airbnb (hospedaje)","Servicio de alimentos para empresas"]},
  {n:44,type:"servicio",h:"Salud, belleza y veterinaria",i:["Medicina y consulta mÃƒÂ©dica","ClÃƒÂ­nica","Hospital","Servicios de salud","Veterinaria","PeluquerÃƒÂ­a","EstÃƒÂ©tica","SalÃƒÂ³n de belleza","Spa","Masajes","Fisioterapia","PsicologÃƒÂ­a","OdontologÃƒÂ­a y dentista","NutriciÃƒÂ³n","EnfermerÃƒÂ­a","Acupuntura","Tatuajes","MicropigmentaciÃƒÂ³n","Microblading","DepilaciÃƒÂ³n","CosmetologÃƒÂ­a","Bienestar","QuiroprÃƒÂ¡ctica","Terapias alternativas","Medicina estÃƒÂ©tica","CirugÃƒÂ­a estÃƒÂ©tica","Trasplante capilar","OptometrÃƒÂ­a","PodologÃƒÂ­a","JardinerÃƒÂ­a profesional"]},
  {n:45,type:"servicio",h:"Servicios jurÃƒÂ­dicos y de seguridad",i:["Abogados","Servicios jurÃƒÂ­dicos","NotarÃƒÂ­a","Registro de marcas","ProtecciÃƒÂ³n de datos","AsesorÃƒÂ­a legal","Contratos","ConsultorÃƒÂ­a legal","Servicios de seguridad","Guardia de seguridad","Vigilancia","Alarmas y sistemas de seguridad","Custodia de valores","Servicios funerarios","Cuidado de niÃƒÂ±os","Patentes y propiedad intelectual","Litigios","MediaciÃƒÂ³n y arbitraje","Derecho corporativo","Derecho laboral","GestorÃƒÂ­a","Servicios de detective","ProtecciÃƒÂ³n personal","Servicios de redes sociales en lÃƒÂ­nea"]},
];

let _giroFilter = 'all';
let _openGiroClasses = new Set();

function renderGiroGrid(){
  const grid = document.getElementById('giro-grid');
  if(!grid) return;
  const q = (document.getElementById('giro-search')?.value||'').toLowerCase().trim();
  const isSearch = q.length > 1;

  let data = NIZA_DATA;
  if(_giroFilter==='producto') data = data.filter(c=>c.type==='producto');
  else if(_giroFilter==='servicio') data = data.filter(c=>c.type==='servicio');

  let visible = data.map(cls=>{
    if(!isSearch) return {cls, matchItems:cls.i, headMatch:false, hasMatch:true};
    const headMatch = cls.h.toLowerCase().includes(q) || String(cls.n)===q;
    const matchItems = cls.i.filter(item=>item.toLowerCase().includes(q));
    return {cls, matchItems, headMatch, hasMatch: headMatch||matchItems.length>0};
  }).filter(r=>r.hasMatch);

  if(!visible.length){
    grid.innerHTML = '<div class="giro-hint">Sin resultados para <strong style="color:var(--text)">'+q+'</strong><br><span style="font-size:11px">Prueba con otra palabra clave</span></div>';
    return;
  }

  const hl = (text)=>{
    if(!isSearch||!q) return text;
    const lo = text.toLowerCase(), idx = lo.indexOf(q);
    if(idx<0) return text;
    return text.slice(0,idx)+'<mark>'+text.slice(idx,idx+q.length)+'</mark>'+text.slice(idx+q.length);
  };

  grid.innerHTML = visible.map(({cls,matchItems,headMatch})=>{
    const isOpen = isSearch ? true : _openGiroClasses.has(cls.n);
    const isSel = selectedGiro && selectedGiro.cls===cls.n;
    const pillCls = cls.type==='producto' ? 'prod' : 'serv';
    const pillLabel = cls.type==='producto' ? 'Producto' : 'Servicio';
    const displayItems = isSearch ? (headMatch ? cls.i : matchItems) : cls.i;
    const itemsHtml = displayItems.map(item=>{
      const iItemSel = isSel && selectedGiro.item===item;
      const si = item.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
      const sc = cls.h.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
      return '<span class="giro-chip'+(iItemSel?' selected':'')+'" onclick="selectGiro('+cls.n+',\''+sc+'\',\''+si+'\',\''+cls.type+'\')">'+hl(item)+'</span>';
    }).join('');
    return '<div class="giro-row'+(isOpen?' open':'')+(isSel?' cls-selected':'')+'" id="grow-'+cls.n+'">'
      +'<div class="giro-row-head" onclick="toggleGiroRow('+cls.n+')">'
      +'<span class="giro-num-badge">'+cls.n+'</span>'
      +'<span class="giro-heading-text">'+hl(cls.h)+'</span>'
      +'<span class="giro-type-pill '+pillCls+'">'+pillLabel+'</span>'
      +'<span class="giro-item-count">'+cls.i.length+'</span>'
      +'<span class="giro-chevron">Ã¢â€“Â¾</span>'
      +'</div>'
      +'<div class="giro-items-wrap">'+(itemsHtml||'<span style="color:var(--muted);font-size:11px">Sin coincidencias en esta clase</span>')+'</div>'
      +'</div>';
  }).join('');
}

function toggleGiroRow(n){
  if(_openGiroClasses.has(n)) _openGiroClasses.delete(n);
  else _openGiroClasses.add(n);
  renderGiroGrid();
}

function filterGiros(){ renderGiroGrid(); }

function setGiroFilter(f){
  _giroFilter = f;
  document.getElementById('gfp-all')?.classList.remove('active');
  document.getElementById('gfp-prod')?.classList.remove('active');
  document.getElementById('gfp-serv')?.classList.remove('active');
  const map = {all:'gfp-all',producto:'gfp-prod',servicio:'gfp-serv'};
  if(map[f]) document.getElementById(map[f])?.classList.add('active');
  renderGiroGrid();
}

function selectGiro(cls, category, item, type){
  selectedGiro = {cls, category, description:item, type, item};
  renderGiroGrid();
  const banner = document.getElementById('giro-banner');
  const clsEl  = document.getElementById('gsb-cls-num');
  const catEl  = document.getElementById('gsb-cat-name');
  const descEl = document.getElementById('gsb-cat-desc');
  if(banner) banner.classList.add('show');
  if(clsEl)  clsEl.textContent  = 'Clase '+cls;
  if(catEl)  catEl.textContent  = item;
  if(descEl) descEl.textContent = 'Clase Niza '+cls+' Ã¢â‚¬â€ '+category;
  setTimeout(()=>{ document.getElementById('btn-continuar-2')?.scrollIntoView({behavior:'smooth',block:'nearest'}); },150);
}

function clearGiro(){
  selectedGiro = null;
  _openGiroClasses.clear();
  renderGiroGrid();
  const banner = document.getElementById('giro-banner');
  if(banner) banner.classList.remove('show');
}

(function(){ renderGiroGrid(); })();

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// ANALYSIS TYPE SELECTION
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function toggleAnalysis(type){
  selectedAnalysis[type] = !selectedAnalysis[type];
  const card=document.getElementById('at-'+type);
  const chk=document.getElementById('ac-'+type);
  if(card) card.classList.toggle('selected', selectedAnalysis[type]);
  if(chk){ if(selectedAnalysis[type]) chk.classList.add('selected'); else chk.classList.remove('selected'); }
  // Show/hide step 2 (Giro) based on marca selection
  const wc2=document.getElementById('wc-2');
  const wl2=document.getElementById('wl-2');
  if(wc2) wc2.style.opacity = selectedAnalysis.marca ? '1':'0.3';
  if(wl2) wl2.style.opacity = selectedAnalysis.marca ? '1':'0.3';
}
// init checkmarks
document.querySelectorAll('.at-check').forEach(c=>c.classList.add('selected'));

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// BRAND MANAGEMENT
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function addBrand(){
  syncBrandList();
  if(brandList.length>=10){showToast('MÃƒÂ¡ximo 10 marcas');return;}
  brandList.push('');
  renderBrandList();
}
function removeBrand(idx){
  if(brandList.length<=1){showToast('MÃƒÂ­nimo una marca','info');return;}
  brandList.splice(idx,1);
  renderBrandList();
}
function syncBrandList(){
  document.querySelectorAll('.brand-input').forEach((inp,i)=>{ brandList[i]=inp.value.trim(); });
}
function renderBrandList(){
  const el=document.getElementById('brand-list');
  el.innerHTML=brandList.map((b,i)=>{
    const saved=b&&favorites.includes(b);
    return `<div class="brand-row" data-idx="${i}">
      <span class="brand-num">${i+1}</span>
      <input type="text" class="brand-input" value="${b}" placeholder="Ej. QUANTUM TECH"
        autocomplete="off" spellcheck="false"
        oninput="brandList[${i}]=this.value.trim()"/>
      ${brandList.length>1?`<button class="btn-del-brand" onclick="removeBrand(${i})">Ã¢Å“â€¢</button>`:''}
    </div>`;
  }).join('');
  const inputs=el.querySelectorAll('.brand-input');
  if(inputs.length) inputs[inputs.length-1].focus();
  if(perBrandMode) renderPbPickers();
}
function starBrand(idx){
  syncBrandList();
  const name=(brandList[idx]||'').trim();
  if(!name){showToast('Escribe el nombre primero','info');return;}
  toggleFavorite(name);
}
function updateStars(){
  document.querySelectorAll('.brand-input').forEach((inp,i)=>{
    const btn=document.getElementById('star-'+i); if(!btn)return;
    const v=inp.value.trim();
    const s=v&&favorites.includes(v);
    btn.textContent=s?'Ã¢Ëœâ€¦':'Ã¢Ëœâ€ ';
    btn.classList.toggle('saved',s);
  });
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// FAVORITES
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function toggleFavorite(brand){
  const idx=favorites.indexOf(brand);
  if(idx>=0){favorites.splice(idx,1);showToast(brand+' removida','info');}
  else{favorites.push(brand);showToast('Ã¢Ëœâ€¦ '+brand+' guardada','info');}
  localStorage.setItem('tim_fav',JSON.stringify(favorites));
  renderFavGrid(); updateFavBadge(); updateStars();
}
function renderFavGrid(){
  const g=document.getElementById('fav-grid');
  if(!g)return;
  if(!favorites.length){g.innerHTML='<span class="fav-empty">Sin marcas guardadas</span>';return;}
  g.innerHTML=favorites.map(b=>`<span class="fav-chip" onclick="prefillBrand('${b.replace(/'/g,"\\'")}')">
    Ã¢Ëœâ€¦ ${b}
    <span class="fav-chip-del" onclick="event.stopPropagation();toggleFavorite('${b.replace(/'/g,"\\'")}')">Ã¢Å“â€¢</span>
  </span>`).join('');
}
function updateFavBadge(){
  const b=document.getElementById('fav-badge');
  if(b) b.textContent=favorites.length?'('+favorites.length+' guardadas)':'';
}
function prefillBrand(name){
  syncBrandList();
  const ei=brandList.findIndex(b=>!b.trim());
  if(ei>=0){brandList[ei]=name;}else{brandList.push(name);}
  renderBrandList();
  showToast('"'+name+'" aÃƒÂ±adida','info');
}
function saveSession(){
  try{localStorage.setItem('tim_session',JSON.stringify({brandResults,favorites,criteriaConfig,criteriaMode,ts:Date.now()}));showToast('SesiÃƒÂ³n guardada','info');}catch(e){showToast('Error al guardar');}
}
function loadSession(){
  try{
    const raw=localStorage.getItem('tim_session');
    if(!raw){showToast('Sin sesiÃƒÂ³n guardada','info');return;}
    const s=JSON.parse(raw);
    if(!confirm('Cargar sesiÃƒÂ³n del '+new Date(s.ts).toLocaleString()+'?'))return;
    brandResults=s.brandResults||{};
    favorites=s.favorites||[];
    criteriaConfig={...CRITERIA_DEFAULT,...(s.criteriaConfig||{})};
    criteriaMode=s.criteriaMode||'default';
    setCfgMode(criteriaMode);
    renderFavGrid(); updateFavBadge();
    const brands=Object.values(brandResults).map(b=>b.brand);
    if(brands.length){
      setupTabs(brands);
      Object.keys(brandResults).forEach(i=>{ const br=brandResults[i]; renderBrandTab(Number(i),br.brand,{ompi_rows:br.ompi,impi_rows:br.impi,combined:br.riesgo,conflicto:br.conflicto,hay_concesion_global:br.hay_concesion_global,file:br.file}); });
    }
    showToast('SesiÃƒÂ³n cargada','info');
  }catch(e){showToast('Error al cargar');}
}
function clearSession(){
  if(!confirm('Limpiar seguimiento y sesiÃƒÂ³n guardada?'))return;
  favorites=[];
  localStorage.removeItem('tim_fav');localStorage.removeItem('tim_session');
  renderFavGrid();updateFavBadge();showToast('Limpiado','info');
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// CLASS MODE
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
document.querySelectorAll('.mode-btn').forEach(b=>{
  b.addEventListener('click',()=>{
    document.querySelectorAll('.mode-btn').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');
    selectedMode=b.dataset.mode;
    document.getElementById('manual-wrap').classList.toggle('show',selectedMode==='M');
  });
});
function addClase(){
  const inp=document.getElementById('cls-num');
  const val=parseInt(inp.value);
  const warn=document.getElementById('cls-dup');
  if(!val||val<1||val>45){showToast('Ingresa una clase entre 1 y 45');return;}
  if(selectedClases.includes(val)){warn.classList.add('show');setTimeout(()=>warn.classList.remove('show'),2500);return;}
  warn.classList.remove('show');
  selectedClases.push(val); selectedClases.sort((a,b)=>a-b);
  inp.value=''; inp.focus(); renderClaseChips();
}
function removeClase(v){selectedClases=selectedClases.filter(x=>x!==v);renderClaseChips();}
function clearClases(){selectedClases=[];renderClaseChips();}
function renderClaseChips(){
  const a=document.getElementById('cls-chips');
  if(!selectedClases.length){a.className='cls-chips-area empty';a.innerHTML='';return;}
  a.className='cls-chips-area';
  a.innerHTML=selectedClases.map(v=>`<span class="cls-chip">Clase ${v}<span class="cls-chip-del" onclick="removeClase(${v})">Ã¢Å“â€¢</span></span>`).join('');
}
const _clsNumEl = document.getElementById('cls-num');
if(_clsNumEl) _clsNumEl.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();addClase();}});

// Ã¢â€â‚¬Ã¢â€â‚¬ Per-brand class mode Ã¢â€â‚¬Ã¢â€â‚¬
function togglePbMode(){
  perBrandMode=!perBrandMode;
  const btn=document.getElementById('btn-pbmode');
  const grid=document.getElementById('shared-mode-grid');
  const mw=document.getElementById('manual-wrap');
  const pw=document.getElementById('pb-wrap');
  const ph=document.getElementById('pb-hint');
  btn.classList.toggle('active',perBrandMode);
  grid.style.display=perBrandMode?'none':'';
  if(!perBrandMode){mw.style.display='';pw.classList.remove('show');ph.style.display='none';if(selectedMode==='M')mw.classList.add('show');}
  else{mw.style.display='none';pw.classList.add('show');ph.style.display='block';renderPbPickers();}
}
function renderPbPickers(){
  syncBrandList();
  const pw=document.getElementById('pb-wrap');
  if(!perBrandMode){pw.innerHTML='';return;}
  const brands=brandList.map((b,i)=>({b:b||'Marca '+(i+1),i}));
  pw.innerHTML=brands.map(({b,i})=>{
    const cls=brandClases[i]||[];
    const summary=cls.length?cls.length+' clase(s)':'Todas (1Ã¢â‚¬â€œ45)';
    const hasCls=cls.length>0;
    return `<div class="pb-brand-row">
      <div class="pb-brand-hdr" onclick="togglePbRow(${i})">
        <span class="pb-brand-num">${i+1}</span>
        <span class="pb-brand-name">${b}</span>
        <span class="pb-summary${hasCls?' has':''}" id="pb-sum-${i}">${summary}</span>
        <span style="color:var(--muted);font-size:11px" id="pb-chev-${i}">Ã¢â€“Â¾</span>
      </div>
      <div class="pb-brand-body" id="pb-body-${i}">
        <div class="pb-mode-grid" id="pb-mg-${i}">
          <button class="mode-btn${!hasCls?' active':''}" data-pbmode="T" onclick="setPbMode(${i},'T',this)">Todas<span class="mode-sub">1Ã¢â‚¬â€œ45</span></button>
          <button class="mode-btn" data-pbmode="S" onclick="setPbMode(${i},'S',this)">Servicios<span class="mode-sub">35Ã¢â‚¬â€œ45</span></button>
          <button class="mode-btn" data-pbmode="P" onclick="setPbMode(${i},'P',this)">Productos<span class="mode-sub">1Ã¢â‚¬â€œ34</span></button>
          <button class="mode-btn${hasCls?' active':''}" data-pbmode="M" onclick="setPbMode(${i},'M',this)">Manual<span class="mode-sub">Custom</span></button>
        </div>
        <div id="pb-manual-${i}" style="${hasCls?'':'display:none'}">
          <div class="cls-add-row" style="margin-top:10px">
            <input type="number" id="pb-inp-${i}" class="cls-num-input" min="1" max="45" placeholder="1Ã¢â‚¬â€œ45"
              onkeydown="if(event.key==='Enter'){event.preventDefault();addClaseFor(${i});}"/>
            <button class="btn-agregar-clase" onclick="addClaseFor(${i})">+ AGREGAR</button>
            <button class="cls-clear-btn" onclick="clearClasesFor(${i})">Limpiar</button>
          </div>
          <div class="cls-chips-area${hasCls?'':' empty'}" id="pb-chips-${i}"></div>
          <div class="cls-dup-warn" id="pb-dup-${i}">Ã¢Å¡Â  Ya seleccionada</div>
        </div>
      </div>
    </div>`;
  }).join('');
  brands.forEach(({i})=>{if(brandClases[i]&&brandClases[i].length)renderClasesFor(i);});
}
function togglePbRow(i){
  const b=document.getElementById('pb-body-'+i);
  const c=document.getElementById('pb-chev-'+i);
  const open=b.classList.toggle('open');
  if(c)c.style.transform=open?'rotate(180deg)':'';
}
function setPbMode(i,mode,btn){
  brandModes[i]=mode;
  const g=document.getElementById('pb-mg-'+i);
  if(g)g.querySelectorAll('.mode-btn').forEach(b=>b.classList.toggle('active',b.dataset.pbmode===mode));
  const m=document.getElementById('pb-manual-'+i);
  if(m)m.style.display=mode==='M'?'block':'none';
  if(mode!=='M')clearClasesFor(i);
  updatePbSum(i);
}
function addClaseFor(i){
  if(!brandClases[i])brandClases[i]=[];
  const inp=document.getElementById('pb-inp-'+i);
  const warn=document.getElementById('pb-dup-'+i);
  const val=parseInt(inp.value);
  if(!val||val<1||val>45){showToast('Clase entre 1 y 45');return;}
  if(brandClases[i].includes(val)){warn.classList.add('show');setTimeout(()=>warn.classList.remove('show'),2500);return;}
  warn.classList.remove('show');
  brandClases[i].push(val); brandClases[i].sort((a,b)=>a-b);
  brandModes[i]='M';
  const g=document.getElementById('pb-mg-'+i);
  if(g)g.querySelectorAll('.mode-btn').forEach(b=>b.classList.toggle('active',b.dataset.pbmode==='M'));
  const m=document.getElementById('pb-manual-'+i); if(m)m.style.display='block';
  inp.value=''; inp.focus(); renderClasesFor(i); updatePbSum(i);
}
function removeClaseFor(i,v){if(!brandClases[i])return;brandClases[i]=brandClases[i].filter(x=>x!==v);renderClasesFor(i);updatePbSum(i);}
function clearClasesFor(i){brandClases[i]=[];renderClasesFor(i);updatePbSum(i);}
function renderClasesFor(i){
  const a=document.getElementById('pb-chips-'+i); if(!a)return;
  const cls=brandClases[i]||[];
  if(!cls.length){a.className='cls-chips-area empty';a.innerHTML='';return;}
  a.className='cls-chips-area';
  a.innerHTML=cls.map(v=>`<span class="cls-chip">Clase ${v}<span class="cls-chip-del" onclick="removeClaseFor(${i},${v})">Ã¢Å“â€¢</span></span>`).join('');
}
function updatePbSum(i){
  const s=document.getElementById('pb-sum-'+i); if(!s)return;
  const cls=brandClases[i]||[];
  const mode=brandModes[i]||'T';
  if(mode==='M'&&cls.length){s.textContent=cls.length+' clase(s) Ã‚Â· '+cls.join(', ');s.className='pb-summary has';}
  else if(mode==='T'){s.textContent='Todas (1Ã¢â‚¬â€œ45)';s.className='pb-summary';}
  else if(mode==='S'){s.textContent='Servicios (35Ã¢â‚¬â€œ45)';s.className='pb-summary';}
  else if(mode==='P'){s.textContent='Productos (1Ã¢â‚¬â€œ34)';s.className='pb-summary';}
  else{s.textContent='Sin clases';s.className='pb-summary';}
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// CRITERIA CONFIG
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function setCfgMode(mode){
  criteriaMode=mode;
  const cd=document.getElementById('cfg-def');if(cd)cd.classList.toggle('active',mode==='default');
  const cc=document.getElementById('cfg-cus');if(cc)cc.classList.toggle('active',mode==='custom');
  const sw=document.getElementById('sliders-wrap');if(sw)sw.classList.toggle('show',mode==='custom');
  if(mode==='default'){criteriaConfig={...CRITERIA_DEFAULT};syncSliders();}
  Object.keys(brandResults).forEach(i=>recompute(Number(i)));
}
function updateSlider(key,val){criteriaConfig[key]=Number(val);syncSliders();Object.keys(brandResults).forEach(i=>recompute(Number(i)));}
function stepCrit(delta){criteriaConfig.minCount=Math.max(1,Math.min(4,criteriaConfig.minCount+delta));document.getElementById('crit-val').textContent=criteriaConfig.minCount;Object.keys(brandResults).forEach(i=>recompute(Number(i)));}
function resetCrit(){criteriaConfig={...CRITERIA_DEFAULT};syncSliders();Object.keys(brandResults).forEach(i=>recompute(Number(i)));}
function syncSliders(){
  const c=criteriaConfig;
  ['dist','sim','conf','conc'].forEach(k=>{const s=document.getElementById('sl-'+k);if(s)s.value=c[k];});
  const dv=document.getElementById('dv-dist');if(dv)dv.textContent='Ã¢â€°Â¤'+c.dist+'%';
  const sv=document.getElementById('dv-sim');if(sv)sv.textContent='Ã¢â€°Â¥'+c.sim+'%';
  const cv=document.getElementById('dv-conf');if(cv)cv.textContent='Ã¢â€°Â¥'+c.conf+'%';
  const nv=document.getElementById('dv-conc');if(nv)nv.textContent='Ã¢â€°Â¤'+c.conc+'%';
  const cvn=document.getElementById('crit-val');if(cvn)cvn.textContent=c.minCount;
  ['mc1','mc2','mc3','mc4'].forEach((id,idx)=>{const el=document.getElementById(id);if(!el)return;const vals=['Ã¢â€°Â¤'+c.dist+'%','Ã¢â€°Â¥'+c.sim+'%','Ã¢â€°Â¥'+c.conf+'%','Ã¢â€°Â¤'+c.conc+'%'];el.textContent=vals[idx];});
  const r=document.getElementById('mc-rule');if(r)r.textContent='Ã¢â€°Â¤'+(c.minCount-1)+' criterio'+(c.minCount-1!==1?'s':'')+' activo'+(c.minCount-1!==1?'s':'');
  const m=document.getElementById('mc-min');if(m)m.textContent=c.minCount;
}
function evalClient(r){
  const c=criteriaConfig;
  let dist=r.Distancia??1, sim=r.Similitud??0, probConf=r.Prob_Conf??0, probConc=r.Prob_Conc??1;
  // Name-similarity override: if normalized brand names match closely, boost probConf
  // (catches case/punctuation variants like "Greater One" vs "GREATER.ONE")
  if(r._brandNew && r.Marca){
    const clean=s=>s.toLowerCase().replace(/[^a-z0-9]/g,'');
    const bn=clean(r._brandNew), em=clean(r.Marca);
    if(bn&&em&&(bn===em||bn.includes(em)||em.includes(bn))){
      probConf=Math.max(probConf,0.9);
    }
  }
  const c1=dist<=c.dist/100;
  const c2=sim>=c.sim/100;
  const c3=probConf>=c.conf/100;
  const c4=probConc<=c.conc/100;
  const active=[c1,c2,c3,c4].filter(Boolean).length;
  const parts=[];
  if(c1)parts.push('C1:DistÃ¢â€°Â¤'+c.dist+'%');if(c2)parts.push('C2:SimÃ¢â€°Â¥'+c.sim+'%');
  if(c3)parts.push('C3:ConfÃ¢â€°Â¥'+c.conf+'%');if(c4)parts.push('C4:ConcÃ¢â€°Â¤'+c.conc+'%');
  return{hay_concesion:active<c.minCount,criterios_activos:active,criterios_texto:parts.join(' Ã‚Â· ')||'Ninguno'};
}
function recompute(idx){
  const br=brandResults[idx]; if(!br)return;
  const rc=br.riesgo.map(r=>({...r,_brandNew:br.brand,...evalClient({...r,_brandNew:br.brand})}));
  const seen=new Set(),cf=[],cm={};
  rc.forEach(r=>{
    if(!r.hay_concesion){
      const key=r.Marca+'|'+r.Registro+'|'+r.Origen;
      if(!cm[key])cm[key]=new Set();
      cm[key].add(String(r.Clase));
      if(!seen.has(key)){seen.add(key);cf.push({Marca:r.Marca,Registro:r.Registro,Origen:r.Origen,Clases:''});}
    }
  });
  cf.forEach(it=>{const k=it.Marca+'|'+it.Registro+'|'+it.Origen;it.Clases=[...cm[k]].sort().join(', ');});
  const hay=rc.length===0||rc.every(r=>r.hay_concesion);
  br.riesgoComputed=rc; br.conflictoComputed=cf; br.hay_concesion_global=hay;
  renderConflictoFor(idx,br.brand,cf,rc,hay);
  // Update KPIs
  const cf4=rc.filter(r=>!r.hay_concesion&&(r.criterios_activos??0)===4).length;
  const impiEl=document.getElementById('k-impi-'+idx); if(impiEl)impiEl.textContent=(br.impi||[]).length;
  const cfEl=document.getElementById('k-cf-'+idx); if(cfEl)cfEl.textContent=cf.length;
  const cf4El=document.getElementById('k-cf4-'+idx); if(cf4El)cf4El.textContent=cf4;
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// ANALYSIS START
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
const STEPS=[
  {id:'model',label:'Modelo ML',match:/Entrenando|Modelo listo/i,pct:15},
  {id:'impi',label:'IMPI',match:/Iniciando scraping IMPI|Marcanet/i,pct:55},
  {id:'impi2',label:'IMPI datos',match:/registros IMPI|IMPI omitida/i,pct:80},
  {id:'excel',label:'Reporte',match:/Generando Excel|guardado/i,pct:92},
  {id:'done',label:'Listo',match:/Archivo guardado|COMPLETADO/i,pct:100}
];

function startAnalysis(){
  syncBrandList();
  const brands=brandList.filter(b=>b.trim());
  if(!brands.length){showToast('Ingresa al menos una marca');return;}

  // If marca analysis selected, require a giro to be selected
  if(selectedAnalysis.marca && !selectedGiro){
    showToast('Selecciona el giro de tu negocio en el paso anterior');return;
  }

  // Build class config from selected giro (always Manual with the single Niza class)
  const giroMode = selectedGiro ? 'M' : 'T';
  const giroRaw  = selectedGiro ? String(selectedGiro.cls) : '';

  let classArr=[];
  for(let i=0;i<brands.length;i++) classArr.push({mode:giroMode, raw:giroRaw});

  const skipOmpi=true;
  const skipImpi=false;
  const headed=false;

  brandResults={};
  const btn=document.getElementById('run-btn');
  btn.disabled=true; btn.innerHTML='<span class="spinner"></span>ANALIZANDOÃ¢â‚¬Â¦';

  setupTabs(brands);

  let chain=Promise.resolve();
  brands.forEach((brand,idx)=>{
    const {mode,raw}=classArr[idx];
    chain=chain.then(()=>runBrand(brand,idx,raw,skipOmpi,skipImpi,headed,mode));
  });
  chain.then(()=>{btn.disabled=false;btn.innerHTML='Ã¢â€“Â¶ LANZAR ANÃƒÂLISIS';});
}

function setupTabs(brands){
  const ra=document.getElementById('results-area');
  ra.style.display='block';
  ra.scrollIntoView({behavior:'smooth',block:'start'});
  const wrap=document.getElementById('brand-tabs-wrap');
  const bar=document.getElementById('btabs-bar');
  const contents=document.getElementById('btabs-contents');
  const ca=document.getElementById('compare-area');
  wrap.style.display=brands.length>1?'block':'none';
  bar.innerHTML=''; contents.innerHTML=''; ca.style.display='none'; ca.innerHTML='';
  brands.forEach((brand,idx)=>{
    const tab=document.createElement('div');
    tab.className='btab'+(idx===0?' active':'');
    tab.id='btab-'+idx;
    tab.innerHTML=`<span class="btab-dot" id="bdot-${idx}"></span>${brand}`;
    tab.onclick=(()=>{const i=idx;return()=>switchBrandTab(i);})();
    bar.appendChild(tab);
    const content=document.createElement('div');
    content.className='btab-content'+(idx===0?' active':'');
    content.id='btab-c-'+idx;
    content.innerHTML=buildBrandHTML(brand,idx);
    contents.appendChild(content);
  });
  activeBrandIdx=0;
}

function switchBrandTab(idx){
  activeBrandIdx=idx;
  document.querySelectorAll('.btab').forEach((t,i)=>t.classList.toggle('active',t.id==='btab-'+i&&i===idx));
  document.querySelectorAll('.btab-content').forEach((t,i)=>t.classList.toggle('active',i===idx));
  const ca=document.getElementById('compare-area');
  if(ca)ca.style.display='none';
}

function switchToCompare(){
  document.querySelectorAll('.btab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.btab-content').forEach(t=>t.classList.remove('active'));
  document.getElementById('btab-compare')?.classList.add('active');
  const ca=document.getElementById('compare-area');
  if(ca){ca.style.display='block';buildCompareView();}
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// BRAND HTML TEMPLATE
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function buildBrandHTML(brand,idx){
  return `
  <!-- Progress -->
  <div class="prog-wrap" id="pw-${idx}" style="margin-top:16px">
    <div class="prog-header">
      <span class="prog-label" id="pl-${idx}">Iniciando...</span>
      <span class="prog-eta" id="pe-${idx}"></span>
    </div>
    <div class="prog-track"><div class="prog-bar" id="pb-${idx}"></div></div>
    <div class="prog-detail" id="pd-${idx}"></div>
    <div class="prog-steps" id="ps-${idx}"></div>
  </div>

  <!-- Export All -->
  <div id="exp-${idx}" style="display:none;text-align:right;margin:8px 0 4px">
    <button class="btn-sm" onclick="exportAll(${idx})" style="background:var(--blue)">Ã¢â€ â€œ EXPORTAR TODO - XLSX</button>
  </div>

  <!-- 2x2 Results Grid -->
  <div class="results-grid-2x2">

    <!-- Registro Legal de Marca -->
    <div class="result-panel" id="acc-marca-${idx}" style="display:none">
      <div class="result-panel-hdr">
        <span class="result-panel-title">Registro Legal de Marca</span>
        <span class="aa-status-badge" id="aab-marca-${idx}" style="display:none"></span>
        <button class="btn-sm outline" onclick="exportFor(${idx},'conflicto')" style="flex-shrink:0;margin-left:8px">Ã¢â€ â€œ XLSX</button>
      </div>
      <div class="result-panel-body" id="aab-body-marca-${idx}">
        <div class="kpi-strip" id="kpi-${idx}">
          <div class="kpi-item"><div class="kpi-label">Marcas IMPI</div><div class="kpi-num blue" id="k-impi-${idx}">Ã¢â‚¬â€</div></div>
          <div class="kpi-item"><div class="kpi-label">Conflictos Totales</div><div class="kpi-num red" id="k-cf-${idx}">Ã¢â‚¬â€</div></div>
          <div class="kpi-item"><div class="kpi-label">CrÃƒÂ­ticos (4/4)</div><div class="kpi-num red" id="k-cf4-${idx}">Ã¢â‚¬â€</div></div>
          <div class="kpi-item"><div class="kpi-label">Resultado</div><div class="kpi-num" id="k-risk-${idx}" style="font-size:12px;line-height:1.3;white-space:nowrap">Ã¢â‚¬â€</div></div>
        </div>
        <div class="rs" id="rs-cf-${idx}">
          <div class="rs-hdr">
            <div class="rs-icon" id="cf-icon-${idx}" style="background:var(--red-bg);font-size:11px">!</div>
            <span class="rs-title" id="cf-title-${idx}">Marcas en Conflicto</span>
            <span class="rs-count" id="cnt-cf-${idx}">Ã¢â‚¬â€</span>
            <div class="rs-actions">
              <button class="btn-sm" onclick="exportFor(${idx},'conflicto')">Ã¢â€ â€œ XLSX</button>
            </div>
          </div>
          <div class="conf-status-bar" id="cf-bar-${idx}">
            <span class="cgs-dot" id="cgs-dot-${idx}"></span>
            <span class="cgs-text" id="cgs-txt-${idx}"></span>
            <span style="font-size:11px;color:var(--muted)" id="cgs-sub-${idx}"></span>
          </div>
          <div id="cf-body-${idx}"><div class="empty-state">AnÃƒÂ¡lisis en curso...</div></div>
        </div>
      </div>
    </div>

    <!-- Visible en Redes Sociales -->
    <div class="result-panel" id="acc-social-${idx}" style="display:none">
      <div class="result-panel-hdr">
        <span class="result-panel-title">Visible en Redes Sociales</span>
        <span class="aa-status-badge" id="aab-social-${idx}" style="display:none"></span>
        <button class="btn-sm outline" onclick="exportSocial(${idx})" style="flex-shrink:0;margin-left:8px">Ã¢â€ â€œ XLSX</button>
      </div>
      <div class="result-panel-body">
        <div id="social-body-${idx}"><div class="empty-state">VerificaciÃƒÂ³n en curso...</div></div>
      </div>
    </div>

    <!-- Encontrable en Internet -->
    <div class="result-panel" id="acc-domain-${idx}" style="display:none">
      <div class="result-panel-hdr">
        <span class="result-panel-title">DOMINIOS WEB</span>
        <span class="aa-status-badge" id="aab-domain-${idx}" style="display:none"></span>
        <button class="btn-sm outline" onclick="exportDomain(${idx})" style="flex-shrink:0;margin-left:8px">Ã¢â€ â€œ XLSX</button>
      </div>
      <div class="result-panel-body">
        <div id="domain-body-${idx}"><div class="empty-state">VerificaciÃƒÂ³n en curso...</div></div>
      </div>
    </div>

    <!-- Disponible como Empresa -->
    <div class="result-panel" id="acc-mua-${idx}" style="display:none">
      <div class="result-panel-hdr">
        <span class="result-panel-title">EMPRESAS EXISTENTES</span>
        <span class="aa-status-badge" id="aab-mua-${idx}" style="display:none"></span>
        <button class="btn-sm outline" onclick="exportMua(${idx})" style="flex-shrink:0;margin-left:8px">Ã¢â€ â€œ XLSX</button>
      </div>
      <div class="result-panel-body">
        <div id="mua-body-${idx}"><div class="empty-state">VerificaciÃƒÂ³n en curso...</div></div>
      </div>
    </div>

  </div>

  <!-- SIGA compat (oculto) -->
  <div id="acc-siga-${idx}" style="display:none">
    <div id="aah-siga-${idx}"></div>
    <div id="aab-body-siga-${idx}">
      <div class="siga-period-banner" id="siga-period-${idx}" style="display:none">
        <span class="siga-period-label">PerÃƒÂ­odo analizado:</span>
        <span class="siga-period-range" id="siga-period-range-${idx}"></span>
        <span class="siga-period-dias" id="siga-period-dias-${idx}"></span>
      </div>
      <div class="kpi-strip" id="siga-kpi-${idx}">
        <div class="kpi-item"><div class="kpi-label">Solicitudes</div><div class="kpi-num blue" id="sk-total-${idx}">Ã¢â‚¬â€</div></div>
        <div class="kpi-item"><div class="kpi-label">Clases Niza</div><div class="kpi-num purple" id="sk-clases-${idx}">Ã¢â‚¬â€</div></div>
        <div class="kpi-item"><div class="kpi-label">Conflictos</div><div class="kpi-num red" id="sk-cf-${idx}">Ã¢â‚¬â€</div></div>
        <div class="kpi-item"><div class="kpi-label">Existencia de Riesgo</div><div class="kpi-num" id="sk-risk-${idx}" style="font-size:13px;line-height:1.3;white-space:nowrap">Ã¢â‚¬â€</div></div>
      </div>
      <div class="stats-section" id="siga-stats-${idx}" style="display:none;margin-bottom:14px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
          <div class="card" style="padding:16px">
            <div class="card-title" style="margin-bottom:8px">Criterios de Riesgo</div>
            <div class="chart-canvas-rel"><canvas id="siga-chart-crit-${idx}"></canvas></div>
          </div>
          <div class="card" style="padding:16px">
            <div class="card-title" style="margin-bottom:8px">ProporciÃƒÂ³n de Conflicto</div>
            <div class="chart-canvas-rel"><canvas id="siga-chart-conf-${idx}"></canvas></div>
          </div>
        </div>
        <div id="siga-cls-wrap-${idx}" style="display:none">
          <button class="cls-toggle-btn" id="siga-cls-btn-${idx}" onclick="toggleSigaClsStats(${idx})">
            <span>Desglose por Clase Niza Ã¢â‚¬â€ SIGA</span>
            <span style="font-weight:400;color:var(--muted2)" id="siga-cls-btn-sub-${idx}"></span>
            <span style="margin-left:auto;font-size:10px" id="siga-cls-btn-chev-${idx}">Ã¢â€“Â¾</span>
          </button>
          <div class="cls-charts-grid" id="siga-cls-grid-${idx}"></div>
        </div>
      </div>
      <div class="rs" id="siga-rs-cf-${idx}">
        <div class="rs-hdr">
          <div class="rs-icon" id="siga-cf-icon-${idx}" style="background:var(--red-bg)"></div>
          <span class="rs-title">Marcas en Conflicto Ã¢â‚¬â€ Oposiciones</span>
          <span class="rs-count" id="siga-cnt-cf-${idx}">Ã¢â‚¬â€</span>
          <div class="rs-actions">
            <button class="btn-sm" onclick="exportSigaFor(${idx},'conflicto')">Ã¢â€ â€œ XLSX</button>
          </div>
        </div>
        <div class="conf-status-bar" id="siga-cf-bar-${idx}">
          <span class="cgs-dot" id="siga-cgs-dot-${idx}"></span>
          <span class="cgs-text" id="siga-cgs-txt-${idx}"></span>
          <span style="font-size:11px;color:var(--muted)" id="siga-cgs-sub-${idx}"></span>
        </div>
        <div id="siga-cf-body-${idx}"><div class="empty-state">AnÃƒÂ¡lisis en curso...</div></div>
      </div>
      <div class="rs">
        <div class="rs-hdr">
          <div class="rs-icon" style="background:#fef9c3;color:#854d0e"></div>
          <span class="rs-title">Solicitudes SIGA Ã¢â‚¬â€ AnÃƒÂ¡lisis de Riesgo</span>
          <span class="rs-count" id="siga-cnt-riesgo-${idx}">Ã¢â‚¬â€</span>
          <div class="rs-actions">
            <button class="btn-sm outline" onclick="openCritModal()">Criterios</button>
            <button class="btn-sm" onclick="exportSigaFor(${idx},'riesgo')">Ã¢â€ â€œ XLSX</button>
          </div>
        </div>
        <div class="tbl-wrap" id="siga-tbl-riesgo-${idx}"><div class="empty-state">AnÃƒÂ¡lisis en curso...</div></div>
      </div>
    </div>
  </div>
  `;
}

function toggleAcc(type,idx){
  const hdr=document.getElementById('aah-'+type+'-'+idx);
  const body=document.getElementById('aab-body-'+type+'-'+idx);
  if(!hdr||!body)return;
  const open=body.classList.toggle('open');
  hdr.classList.toggle('open',open);
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// RUN ONE BRAND
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function runBrand(brand,idx,classesRaw,skipOmpi,skipImpi,headed,modeOverride){
  return new Promise(resolve=>{
    const dot=document.getElementById('bdot-'+idx);
    if(dot)dot.className='btab-dot running';
    switchBrandTab(idx);

    const ss={};STEPS.forEach(s=>ss[s.id]='pending');
    const pw=document.getElementById('pw-'+idx);
    if(pw){pw.classList.add('show');document.getElementById('pb-'+idx).style.width='3%';document.getElementById('pl-'+idx).textContent='Iniciando anÃƒÂ¡lisis...';document.getElementById('pe-'+idx).textContent='Estimado: ~2-5 min';}
    renderSteps(idx,ss);

    let elapsed=0;
    const timer=setInterval(()=>{
      elapsed++;
      const pe=document.getElementById('pe-'+idx);
      if(pe){const m=Math.floor(elapsed/60),s=elapsed%60;pe.textContent=`${m}m ${s}s transcurrido`;}
      const pb=document.getElementById('pb-'+idx);
      if(pb){const cur=parseFloat(pb.style.width)||3;pb.style.width=Math.min(cur+0.1,88)+'%';}
    },1000);

    // Show relevant accordions immediately
    ['marca','siga','social','domain','mua'].forEach(type=>{
      const acc=document.getElementById('acc-'+type+'-'+idx);
      if(acc) acc.style.display=selectedAnalysis[type]?'block':'none';
    });
    const hint=document.getElementById('aa-hint-'+idx);
    if(hint)hint.style.display='block';

    if(selectedAnalysis.marca){
      const params=new URLSearchParams({brand,mode:modeOverride||selectedMode,classes_raw:classesRaw,skip_ompi:skipOmpi,skip_impi:skipImpi,headed});
      const es=new EventSource('/stream?'+params);
      es.addEventListener('log',e=>{
        tickSteps(idx,ss,e.data);
        const pd=document.getElementById('pd-'+idx);
        if(pd){const cl=e.data.replace(/[Ã°Å¸â€Â§Ã°Å¸Å’ÂÃ°Å¸â€œÅ Ã¢Å“â€¦Ã¢Å¡Â Ã¯Â¸ÂÃ¢ÂÅ’]/g,'').trim();if(cl.length>3)pd.textContent=cl.slice(0,90);}
      });
      es.addEventListener('done',e=>{
        es.close();clearInterval(timer);
        const d=JSON.parse(e.data);
        finishProg(idx,ss,!!d.error);
        if(dot)dot.className='btab-dot '+(d.error?'err':'ok');
        if(!d.error){
          brandResults[idx]={ompi:d.ompi_rows||[],impi:d.impi_rows||[],riesgo:d.combined||[],conflicto:d.conflicto||[],file:d.file,brand,hay_concesion_global:d.hay_concesion_global};
          renderBrandTab(idx,brand,d);
        }
        // Now run non-marca analyses
        runNonMarca(brand,idx,classesRaw,modeOverride).then(resolve);
      });
      es.onerror=()=>{es.close();clearInterval(timer);finishProg(idx,ss,true);if(dot)dot.className='btab-dot err';runNonMarca(brand,idx,classesRaw,modeOverride).then(resolve);};
    } else {
      clearInterval(timer);
      if(pw)pw.classList.remove('show');
      if(dot)dot.className='btab-dot ok';
      runNonMarca(brand,idx,classesRaw,modeOverride).then(resolve);
    }
  });
}

async function runNonMarca(brand,idx,classesRaw,modeOverride){
  const slug=brand.toLowerCase().replace(/[^a-z0-9._]/g,'');
  const pArr=[];
  if(selectedAnalysis.social) pArr.push(runSocialFor(brand,slug,idx));
  if(selectedAnalysis.domain) pArr.push(runDomainFor(brand,slug,idx));
  if(selectedAnalysis.mua)    pArr.push(runMuaFor(brand,idx));
  await Promise.all(pArr);
  buildCompareTab();
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Social for brand Ã¢â€â‚¬Ã¢â€â‚¬
async function runSocialFor(brand,slug,idx){
  const body=document.getElementById('social-body-'+idx);
  if(body)body.innerHTML='<div class="empty-state">Verificando redes sociales...</div>';
  return new Promise(resolve=>{
    const results={};
    const es=new EventSource('/social_check?username='+encodeURIComponent(slug));
    es.addEventListener('progress',e=>{
      const d=JSON.parse(e.data);
      results[d.platform]=d;
    });
    es.addEventListener('done',()=>{
      es.close();
      renderSocialResults(results,idx);
      resolve();
    });
    es.onerror=()=>{
      es.close();
      if(body)body.innerHTML='<div class="empty-state">Error al verificar redes sociales</div>';
      resolve();
    };
  });
}

const SOCIAL_META={
  github:{label:'GitHub',icon:'Ã°Å¸â€™Â»'},instagram:{label:'Instagram',icon:'Ã°Å¸â€œÂ¸'},
  tiktok:{label:'TikTok',icon:'Ã°Å¸Å½Âµ'},youtube:{label:'YouTube',icon:'Ã¢â€“Â¶Ã¯Â¸Â'},
  pinterest:{label:'Pinterest',icon:'Ã°Å¸â€œÅ’'},twitter_x:{label:'X/Twitter',icon:'Ã°Ââ€¢Â'},
  linkedin:{label:'LinkedIn Co.',icon:'Ã°Å¸â€™Â¼'},threads:{label:'Threads',icon:'Ã°Å¸â€â€”'},
  snapchat:{label:'Snapchat',icon:'Ã°Å¸â€˜Â»'},twitch:{label:'Twitch',icon:'Ã°Å¸Å½Â®'},
  telegram:{label:'Telegram',icon:'Ã¢Å“Ë†Ã¯Â¸Â'},patreon:{label:'Patreon',icon:'Ã°Å¸Å½Â¨'},
  substack:{label:'Substack',icon:'Ã°Å¸â€œÂ'},vimeo:{label:'Vimeo',icon:'Ã°Å¸Å½Â¬'},
  spotify:{label:'Spotify',icon:'Ã°Å¸Å½Â§'},devto:{label:'Dev.to',icon:'Ã°Å¸â€˜Â¨Ã¢â‚¬ÂÃ°Å¸â€™Â»'},
  mixcloud:{label:'Mixcloud',icon:'Ã°Å¸Å½â„¢Ã¯Â¸Â'},strava:{label:'Strava',icon:'Ã°Å¸ÂÆ’'},
  discord:{label:'Discord',icon:'Ã°Å¸Å½Â®'},whatsapp:{label:'WhatsApp Ch.',icon:'Ã°Å¸â€™Â¬'},
  line:{label:'Line',icon:'Ã°Å¸â€™Å¡'},meetup:{label:'Meetup',icon:'Ã°Å¸â€˜Â¥'},
  goodreads:{label:'Goodreads',icon:'Ã°Å¸â€œÅ¡'},houzz:{label:'Houzz',icon:'Ã°Å¸ÂÂ '},
  viber:{label:'Viber',icon:'Ã°Å¸â€œÅ¾'}
};

function renderSocialResults(results,idx){
  socialResultsData[idx]=results;
  const body=document.getElementById('social-body-'+idx);
  if(!body)return;
  const entries=Object.values(results).sort((a,b)=>{
    const o={ocupado:0,indeterminado:1,disponible_probable:2};
    return (o[a.status]??1)-(o[b.status]??1);
  });
  const taken=entries.filter(e=>e.status==='ocupado').length;
  const avail=entries.filter(e=>e.status==='disponible_probable').length;
  // Update badge
  const badge=document.getElementById('aab-social-'+idx);
  if(badge){badge.style.display='';badge.textContent=avail+' disponibles';badge.style.cssText+=';background:var(--green-bg);border-color:var(--green-border);color:var(--green)';}
  body.innerHTML='<div class="tool-result-grid">'+
    entries.map(d=>{
      const m=SOCIAL_META[d.platform]||{label:d.platform,icon:'Ã°Å¸â€â€”'};
      const cls=d.status==='disponible_probable'?'ok':d.status==='ocupado'?'taken':'unknown';
      const txt=d.status==='disponible_probable'?'Ã¢Å“â€ Disponible':d.status==='ocupado'?'Ã¢Å“Ëœ Ocupado':'? Indeterm.';
      return `<div class="tool-card">
        <div class="tc-platform">${m.icon} ${m.label}</div>
        <span class="avail-pill ${cls}">${txt}</span>
        ${d.url?`<div class="tc-url"><a href="${d.url}" target="_blank">${d.url.replace(/https?:\/\//,'').slice(0,38)}</a></div>`:''}
      </div>`;
    }).join('')+'</div>';
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Domain for brand Ã¢â€â‚¬Ã¢â€â‚¬
async function runDomainFor(brand,slug,idx){
  const body=document.getElementById('domain-body-'+idx);
  if(body)body.innerHTML='<div class="empty-state">Verificando dominios...</div>';
  return new Promise(resolve=>{
    const es=new EventSource('/domain_check?term='+encodeURIComponent(slug));
    es.addEventListener('result',e=>{
      const rows=JSON.parse(e.data);
      renderDomainResults(rows,idx);
    });
    es.addEventListener('done',()=>{ es.close(); resolve(); });
    es.onerror=()=>{es.close();if(body)body.innerHTML='<div class="empty-state">Error al verificar dominios</div>';resolve();};
  });
}

function renderDomainResults(rows,idx){
  domainResultsData[idx]=rows;
  const body=document.getElementById('domain-body-'+idx);
  if(!body)return;
  if(!rows.length){body.innerHTML='<div class="empty-state">Sin resultados</div>';return;}
  rows.sort((a,b)=>(a.Estado==='No disponible'?1:0)-(b.Estado==='No disponible'?1:0));
  const avail=rows.filter(r=>r.Estado==='Posible disponible').length;
  const badge=document.getElementById('aab-domain-'+idx);
  if(badge){badge.style.display='';badge.textContent=avail+' posibles';badge.style.cssText+=';background:var(--green-bg);border-color:var(--green-border);color:var(--green)';}
  body.innerHTML='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;margin-top:8px">'+
    rows.map(r=>{
      const ok=r.Estado==='Posible disponible';
      const indet=r.Estado==='Indeterminado';
      return `<div class="domain-card" style="border-left:3px solid ${ok?'var(--green)':indet?'var(--orange)':'var(--red)'}">
        <div><div class="domain-name">${r.Dominio}</div></div>
        <span class="avail-pill ${ok?'ok':indet?'unknown':'taken'}">${ok?'Ã¢Å“â€ Disponible':indet?'? Sin datos':'Ã¢Å“Ëœ Ocupado'}</span>
      </div>`;
    }).join('')+'</div>';
}

// Ã¢â€â‚¬Ã¢â€â‚¬ MUA for brand Ã¢â€â‚¬Ã¢â€â‚¬
async function runMuaFor(brand,idx){
  const body=document.getElementById('mua-body-'+idx);
  if(body)body.innerHTML='<div class="empty-state">Consultando SIEM MUA...</div>';
  return new Promise(resolve=>{
    const es=new EventSource('/mua_check?term='+encodeURIComponent(brand));
    es.addEventListener('result',e=>{
      const rows=JSON.parse(e.data);
      renderMuaResults(rows,idx,brand);
    });
    es.addEventListener('done',()=>{ es.close(); resolve(); });
    es.onerror=()=>{es.close();if(body)body.innerHTML='<div class="empty-state">Error al consultar MUA</div>';resolve();};
  });
}

function renderMuaResults(rows,idx,brand){
  muaResultsData[idx]=rows;
  const body=document.getElementById('mua-body-'+idx);
  if(!body)return;
  const badge=document.getElementById('aab-mua-'+idx);
  if(rows.length===0||!rows[0].Error){
    if(badge){
      badge.style.display='';
      if(!rows.length){badge.textContent='Ã¢Å“â€ Sin coincidencias';badge.style.cssText+=';background:var(--green-bg);border-color:var(--green-border);color:var(--green)';}
      else{badge.textContent=rows.length+' similares';badge.style.cssText+=';background:var(--red-bg);border-color:var(--red-border);color:var(--red)';}
    }
  }
  if(!rows.length){
    body.innerHTML=`<div style="text-align:center;padding:24px;background:var(--green-bg);border:1px solid var(--green-border);border-radius:var(--radius-sm)">
      <div style="font-size:32px;margin-bottom:8px">Ã¢Å“â€</div>
      <div style="font-size:14px;font-weight:600;color:var(--green)">Sin coincidencias en el MUA</div>
      <div style="font-size:12px;color:var(--muted);margin-top:6px">Ã‚Â«${brand}Ã‚Â» no aparece en el registro de empresas</div>
    </div>`;
    return;
  }
  if(rows[0]?.Error){
    body.innerHTML=`<div class="empty-state">Ã¢Å¡Â  ${rows[0].Error}</div>`;return;
  }
  const cols=Object.keys(rows[0]);
  let h=`<div class="tbl-wrap" style="margin-top:8px"><table><thead><tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr></thead><tbody>`;
  rows.forEach(r=>{h+=`<tr>${cols.map(c=>`<td>${r[c]||''}</td>`).join('')}</tr>`;});
  h+='</tbody></table></div>';
  body.innerHTML=h;
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// SIGA Ã¢â‚¬â€ RASTREO DE OPOSICIÃƒâ€œN
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
async function runSigaFor(brand,idx,classesRaw,modeOverride){
  const body=document.getElementById('siga-cf-body-'+idx);
  if(body)body.innerHTML='<div class="empty-state"><span class="spinner"></span> Consultando Gaceta Marcaria SIGA IMPI...</div>';
  const tbl=document.getElementById('siga-tbl-riesgo-'+idx);
  if(tbl)tbl.innerHTML='<div class="empty-state"><span class="spinner"></span> Procesando solicitudes...</div>';
  return new Promise(resolve=>{
    const params=new URLSearchParams({brand,mode:modeOverride||selectedMode,classes_raw:classesRaw||''});
    const es=new EventSource('/siga_scan?'+params);
    es.addEventListener('log',e=>{
      const sub=document.getElementById('aas-siga-'+idx);
      const cl=e.data.replace(/[Ã°Å¸â€œâ€¹Ã¢Å“â€¦Ã¢ÂÅ’Ã¢Å¡Â Ã¯Â¸Â]/g,'').trim();
      if(sub&&cl.length>3)sub.textContent=cl.slice(0,80);
    });
    es.addEventListener('done',e=>{
      es.close();
      const d=JSON.parse(e.data);
      if(d.error){
        if(body)body.innerHTML='<div class="empty-state">Ã¢Å¡Â  Error SIGA: '+d.error+'</div>';
        if(tbl)tbl.innerHTML='<div class="empty-state">Sin datos</div>';
        const badge=document.getElementById('aab-siga-'+idx);
        if(badge){badge.style.display='';badge.textContent='Ã¢Å¡Â  Error';badge.style.cssText+=';background:var(--red-bg);border-color:var(--red-border);color:var(--red)';}
        const sub=document.getElementById('aas-siga-'+idx);
        if(sub)sub.textContent='Error al conectar con SIGA IMPI';
        resolve(); return;
      }
      sigaResults[idx]=d;
      renderSigaTab(idx,brand,d);
      resolve();
    });
    es.onerror=()=>{
      es.close();
      if(body)body.innerHTML='<div class="empty-state">Ã¢Å¡Â  No se pudo conectar con SIGA</div>';
      if(tbl)tbl.innerHTML='<div class="empty-state">Sin datos</div>';
      resolve();
    };
  });
}

function renderSigaTab(idx,brand,d){
  const combined   = d.combined || [];
  const conflicto  = d.conflicto || [];
  const hay        = d.hay_concesion_global !== false;
  const fechaMin   = d.fecha_min || '';
  const fechaMax   = d.fecha_max || '';
  const diasAtras  = d.dias_atras || 30;

  // Recompute with current criteria
  const rc = combined.map(r=>({...r,_brandNew:brand,...evalClient({...r,_brandNew:brand})}));
  const seen=new Set(), cf=[], cm={};
  rc.forEach(r=>{
    if(!r.hay_concesion){
      const k=r.Marca+'|'+r.Registro+'|SIGA';
      if(!cm[k])cm[k]=new Set();
      cm[k].add(String(r.Clase));
      if(!seen.has(k)){seen.add(k);cf.push({Marca:r.Marca,Registro:r.Registro,Origen:'SIGA',Clases:''});}
    }
  });
  cf.forEach(it=>{const k=it.Marca+'|'+it.Registro+'|SIGA';it.Clases=[...cm[k]].sort().join(', ');});
  const hayFinal = rc.length===0 || rc.every(r=>r.hay_concesion);
  sigaResults[idx]={...d, combined:rc, conflicto:cf, hay_concesion_global:hayFinal};

  // Period banner
  const banner=document.getElementById('siga-period-'+idx);
  const rangeEl=document.getElementById('siga-period-range-'+idx);
  const diasEl=document.getElementById('siga-period-dias-'+idx);
  if(banner&&(fechaMin||fechaMax)){
    banner.style.display='flex';
    if(rangeEl)rangeEl.textContent=(fechaMin&&fechaMax&&fechaMin!==fechaMax)?fechaMin+' Ã¢â€ â€™ '+fechaMax:(fechaMin||fechaMax);
    if(diasEl)diasEl.textContent='ÃƒÅ¡ltimos '+diasAtras+' dÃƒÂ­as Ã‚Â· '+d.total_registros+' solicitudes en Gaceta';
  }

  // KPIs
  const allCls=[...new Set(rc.map(r=>String(r.Clase||'')).filter(Boolean))];
  const clsWithConflict=allCls.filter(cls=>rc.some(r=>String(r.Clase)===cls&&!r.hay_concesion));
  document.getElementById('sk-total-'+idx).textContent=d.total_registros||rc.length;
  document.getElementById('sk-clases-'+idx).textContent=allCls.length+' clase'+(allCls.length!==1?'s':'');
  document.getElementById('sk-cf-'+idx).textContent=cf.length;
  const riskEl=document.getElementById('sk-risk-'+idx);
  if(riskEl){
    let riskText,riskCls;
    if(cf.length===0){riskText='Sin Existencia de Riesgo';riskCls='green';}
    else if(allCls.length>1&&clsWithConflict.length<allCls.length){riskText='Existencia de Riesgo Parcial';riskCls='orange';}
    else{riskText='Existencia de Riesgo';riskCls='red';}
    riskEl.textContent=riskText;
    riskEl.className='kpi-num '+riskCls;
  }

  // Sub-label
  const sub=document.getElementById('aas-siga-'+idx);
  if(sub)sub.textContent='SIGA Ã‚Â· '+rc.length+' solicitudes analizadas'+(fechaMax?' Ã‚Â· hasta '+fechaMax:'');

  // Charts
  renderSigaStats(idx,rc);

  // Conflicto cards
  renderSigaConflicto(idx,brand,cf,rc,hayFinal);

  // Risk table
  renderSigaRiesgoFor(idx,rc);

  // Badge
  const badge=document.getElementById('aab-siga-'+idx);
  if(badge){
    badge.style.display='';
    badge.textContent=hayFinal?'Ã¢Å“â€ Sin conflictos':'Ã¢Å¡Â  '+cf.length+' conflicto'+(cf.length!==1?'s':'');
    const isOk=hayFinal;
    badge.style.cssText=badge.style.cssText+(isOk?';background:var(--green-bg);border-color:var(--green-border);color:var(--green)':';background:var(--red-bg);border-color:var(--red-border);color:var(--red)');
  }
}

function renderSigaStats(idx,riesgo){
  const sec=document.getElementById('siga-stats-'+idx);
  if(sec)sec.style.display='block';
  if(!riesgo.length)return;
  const conflicts=riesgo.filter(r=>!r.hay_concesion).length;
  const clean=riesgo.length-conflicts;
  const pctRaw=riesgo.length?conflicts/riesgo.length*100:0;
  const pctLabel=conflicts===0?'0%':(Math.round(pctRaw)===0?'<1%':Math.round(pctRaw)+'%');

  // Criteria bar
  const buckets=[0,0,0,0,0];
  riesgo.forEach(r=>buckets[Math.min(r.criterios_activos??0,4)]++);
  mkChart('siga-chart-crit-'+idx,{type:'bar',data:{labels:['0','1','2','3','4'],datasets:[{data:buckets,backgroundColor:[CCC.green,CCC.muted,CCC.orange,CCC.red,CCC.red],borderRadius:4}]},options:{...BOPTS,scales:{x:{ticks:{color:'#6b7a9a',font:{size:9,family:'IBM Plex Mono'}},grid:{color:CCC.grid},title:{display:true,text:'Criterios activos',color:'#6b7a9a',font:{size:9}}},y:{ticks:{color:'#6b7a9a',font:{size:9,family:'IBM Plex Mono'}},grid:{color:CCC.grid},beginAtZero:true}},plugins:{...BOPTS.plugins,legend:{display:false},tooltip:{callbacks:{label:ctx=>` ${ctx.parsed.y} solicitudes`}}}}});

  // Conflict doughnut
  const minSlice=riesgo.length*0.03;
  const dispConflicts=conflicts>0?Math.max(conflicts,minSlice):0;
  mkChart('siga-chart-conf-'+idx,{type:'doughnut',data:{labels:['Sin conflicto ('+clean+')','En conflicto ('+conflicts+')'],datasets:[{data:[riesgo.length-dispConflicts,dispConflicts],backgroundColor:[CCC.green,CCC.red],borderColor:'#f3f6fb',borderWidth:3}]},options:{...BOPTS,cutout:'66%',plugins:{...BOPTS.plugins,tooltip:{callbacks:{label:ctx=>{const realVal=ctx.dataIndex===0?clean:conflicts;const p=riesgo.length?(realVal/riesgo.length*100).toFixed(1):0;return ' '+ctx.label+': '+p+'%';}}}}}});
  setCenterLabel('siga-chart-conf-'+idx,pctLabel,conflicts===0?'libre':'conflictos');

  // Per-class breakdown
  const classes=[...new Set(riesgo.map(r=>String(r.Clase||'')).filter(Boolean))];
  const wrap=document.getElementById('siga-cls-wrap-'+idx);
  if(wrap)wrap.style.display=classes.length>=2?'block':'none';
  if(classes.length>=2)renderSigaPerClassStats(idx,riesgo);
}

function renderSigaPerClassStats(idx,riesgo){
  const clsStats=[...new Set(riesgo.map(r=>String(r.Clase||'')).filter(Boolean))].map(cls=>{
    const rows=riesgo.filter(r=>String(r.Clase)===cls);
    const cf=rows.filter(r=>!r.hay_concesion);
    const pctR=rows.length?cf.length/rows.length*100:0;
    return{cls,rows,cf,pct:Math.round(pctR),pctLabel:cf.length===0?'0%':(Math.round(pctR)===0?'<1%':Math.round(pctR)+'%')};
  }).sort((a,b)=>a.pct-b.pct);
  const sub=document.getElementById('siga-cls-btn-sub-'+idx);
  if(sub)sub.textContent='('+clsStats.length+' clases Ã‚Â· menorÃ¢â€ â€™mayor riesgo)';
  const grid=document.getElementById('siga-cls-grid-'+idx);
  if(!grid)return;
  grid.innerHTML=clsStats.map(({cls,rows,cf,pctLabel})=>`<div class="cls-stat-card">
    <div style="font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:4px">Clase ${cls}</div>
    <div style="font-size:11px;color:var(--muted2);margin-bottom:10px">${rows.length} solicitudes</div>
    <div class="cls-chart-canvas"><canvas id="siga-cc-${idx}-${cls}"></canvas></div>
    <div class="cls-kpis">
      <div class="cls-kpi"><div class="cls-kpi-num ${cf.length?'r':'g'}">${cf.length}</div><div class="cls-kpi-lbl">Conflicto</div></div>
      <div class="cls-kpi"><div class="cls-kpi-num">${rows.length-cf.length}</div><div class="cls-kpi-lbl">Sin conflicto</div></div>
      <div class="cls-kpi"><div class="cls-kpi-num ${cf.length?'r':'g'}">${pctLabel}</div><div class="cls-kpi-lbl">% Riesgo</div></div>
    </div>
  </div>`).join('');
  clsStats.forEach(({cls,rows,cf,pctLabel})=>{
    const clean2=rows.length-cf.length;
    mkChart('siga-cc-'+idx+'-'+cls,{type:'doughnut',data:{labels:['Libre ('+clean2+')','Conflicto ('+cf.length+')'],datasets:[{data:[clean2,cf.length],backgroundColor:[CCC.green,CCC.red],borderColor:'#f3f6fb',borderWidth:2}]},options:{...BOPTS,cutout:'66%',plugins:{...BOPTS.plugins,legend:{labels:{...BOPTS.plugins.legend.labels,font:{size:9,family:'IBM Plex Mono'},boxWidth:8}}}}});
    setCenterLabel('siga-cc-'+idx+'-'+cls,pctLabel,cf.length===0?'libre':'conflictos');
  });
}

function toggleSigaClsStats(idx){
  const g=document.getElementById('siga-cls-grid-'+idx),btn=document.getElementById('siga-cls-btn-'+idx),chev=document.getElementById('siga-cls-btn-chev-'+idx);
  if(!g)return;
  const open=g.classList.toggle('open');
  btn.classList.toggle('open',open);
  if(chev)chev.style.transform=open?'rotate(180deg)':'';
  if(open)setTimeout(()=>{
    const classes=[...document.querySelectorAll('[id^="siga-cc-'+idx+'-"]')].map(c=>c.id.split('-').slice(3).join('-'));
    classes.forEach(cls=>{if(chartInstances['siga-cc-'+idx+'-'+cls])chartInstances['siga-cc-'+idx+'-'+cls].update();});
  },100);
}

function renderSigaConflicto(idx,brand,conflictoRows,riesgoRows,hasConc){
  riesgoRows=riesgoRows||[];
  // Build class data (reuse buildClassData)
  const sigaClsData = buildClassData(conflictoRows,riesgoRows).sort((a,b)=>{
    const pa=a.marks.length/Math.max(a.total,1), pb=b.marks.length/Math.max(b.total,1);
    return pa-pb;
  });
  const totalCf=sigaClsData.filter(c=>c.hasConflict).length;
  const w=document.getElementById('siga-cf-body-'+idx); if(!w)return;

  // Status bar
  const bar=document.getElementById('siga-cf-bar-'+idx);
  if(bar){
    bar.classList.add('show');
    const dot=document.getElementById('siga-cgs-dot-'+idx);
    const txt=document.getElementById('siga-cgs-txt-'+idx);
    const sub=document.getElementById('siga-cgs-sub-'+idx);
    if(hasConc){
      if(dot)dot.className='cgs-dot ok';
      if(txt){txt.className='cgs-text ok';txt.textContent='Ã¢Å“â€ SIN CONFLICTOS EN PROCESO DE CONCESIÃƒâ€œN Ã¢â‚¬â€ Ã‚Â«'+brand+'Ã‚Â»';}
      if(sub)sub.textContent='No se identificaron oposiciones potenciales en la Gaceta Marcaria';
    } else {
      const cfCls=[...new Set(sigaClsData.filter(c=>c.hasConflict).map(c=>c.cls))].join(', ');
      if(dot)dot.className='cgs-dot nok';
      if(txt){txt.className='cgs-text nok';txt.textContent='Ã¢Å¡â€“ OPOSICIÃƒâ€œN POTENCIAL EN CLASE '+cfCls+' Ã¢â‚¬â€ Ã‚Â«'+brand+'Ã‚Â»';}
      if(sub)sub.textContent='Existen solicitudes en proceso que podrÃƒÂ­an oponerse al registro';
    }
  }
  const cnt=document.getElementById('siga-cnt-cf-'+idx);
  if(cnt)cnt.textContent=conflictoRows.length+' marca'+(conflictoRows.length!==1?'s':'');

  if(!sigaClsData.length){w.innerHTML='<div class="empty-state">Sin clases analizadas</div>';return;}
  if(sigaClsData.length===1){w.innerHTML='<div style="padding:16px">'+renderSigaSingleCard(sigaClsData[0])+'</div>';return;}
  w.innerHTML=renderSigaTicker(sigaClsData,idx);
  initSigaTicker(idx);
}

function renderSigaSingleCard(cd){
  const cls=cd.hasConflict?'nok':'ok';
  let h=`<div class="cls-card-single ${cls}"><div class="cls-card-hdr"><span class="cls-badge">CLASE ${cd.cls}</span><span class="cls-status ${cls}" style="font-size:12px;font-weight:600">${cd.hasConflict?'Ã¢Å¡â€“ OPOSICIÃƒâ€œN POTENCIAL':'Ã¢Å“â€ SIN CONFLICTOS'}</span></div>`;
  if(cd.marks.length){
    h+=`<table class="cls-marks-table"><thead><tr><th>DenominaciÃƒÂ³n (SIGA)</th><th>Expediente</th><th>Criterios</th><th>Detalle</th></tr></thead><tbody>`;
    cd.marks.forEach(m=>{
      const cb=m.criterios>=3?'<span class="chip chip-red">'+m.criterios+'/4</span>':m.criterios>=2?'<span class="chip chip-orange">'+m.criterios+'/4</span>':'<span class="chip chip-blue">'+m.criterios+'/4</span>';
      h+=`<tr><td style="font-weight:600;color:var(--red)">${m.marca}</td><td class="mono" style="font-size:10px">${m.registro}</td><td>${cb}</td><td style="font-size:10px;color:var(--muted)">${m.criterios_txt}</td></tr>`;
    });
    h+='</tbody></table>';
  } else {h+='<div style="padding:12px;font-size:12px;color:var(--green)">Ã¢Å“â€ Sin marcas en conflicto</div>';}
  return h+'</div>';
}

const _sigaTickerIdx={}, _sigaTickerActive={}, _sigaClsData={};
function renderSigaTicker(classArr,bidx){
  _sigaClsData[bidx]=classArr;
  const cards=classArr.map((cd,i)=>{const cls=cd.hasConflict?'nok':'ok';return`<div class="cls-mini-card ${cls}" style="min-width:calc(33.33% - 7px)"><div class="cmc-clase">CLASE NIZA</div><div class="cmc-num">${cd.cls}</div><div class="cmc-status ${cls}">${cd.hasConflict?'Ã¢Å¡â€“ '+cd.marks.length+' OPOSICIÃƒâ€œN'+(cd.marks.length!==1?'ES':''):'Ã¢Å“â€ LIBRE'}</div><div class="cmc-count">${cd.hasConflict?'Criterios prom.: '+(cd.marks.length?Math.round(cd.marks.reduce((a,m)=>a+m.criterios,0)/cd.marks.length):0)+'/4':cd.total+' solicitudes'}</div></div>`}).join('');
  const dots=classArr.map((_,i)=>`<div class="t-dot${i===0?' active':''}" onclick="goSigaTicker(${i},${bidx})"></div>`).join('');
  return`<div class="cls-ticker-wrap"><div class="cls-ticker-controls"><span class="cls-ticker-info">${classArr.length} clases Ã‚Â· ordenadas por riesgo Ã¢â€ â€˜</span><div class="cls-ticker-btns"><button class="btn-ticker" onclick="sigaTickerPrev(${bidx})">Ã¢â€ Â</button><button class="btn-ticker" onclick="sigaTickerNext(${bidx},false)">Ã¢â€ â€™</button><button class="btn-ver-todos" onclick="openSigaVtModal(${bidx})">Ã¢ËœÂ° VER TODOS</button></div></div><div class="cls-ticker-viewport" id="siga-tv-${bidx}"><div class="cls-ticker-track" id="siga-tt-${bidx}">${cards}</div></div><div class="cls-ticker-dots" id="siga-td-${bidx}">${dots}</div></div>`;
}
function initSigaTicker(bidx){if(_sigaTickerActive[bidx])clearInterval(_sigaTickerActive[bidx]);_sigaTickerIdx[bidx]=0;_sigaTickerActive[bidx]=setInterval(()=>sigaTickerNext(bidx,true),3500);}
function _sigaTickerVis(bidx){const vp=document.getElementById('siga-tv-'+bidx);if(!vp)return 3;return vp.offsetWidth<600?1:vp.offsetWidth<900?2:3;}
function applySigaTicker(bidx){const tr=document.getElementById('siga-tt-'+bidx),vp=document.getElementById('siga-tv-'+bidx);if(!tr||!vp)return;const vis=_sigaTickerVis(bidx),gap=10,cw=(vp.offsetWidth-(vis-1)*gap)/vis,pos=_sigaTickerIdx[bidx]||0;tr.style.transform=`translateX(-${pos*(cw+gap)}px)`;document.querySelectorAll(`#siga-td-${bidx} .t-dot`).forEach((d,i)=>d.classList.toggle('active',i===pos));}
function sigaTickerNext(bidx,auto){const cd=_sigaClsData[bidx]||[];let pos=_sigaTickerIdx[bidx]||0;const max=Math.max(0,cd.length-_sigaTickerVis(bidx));if(pos>=max){if(auto)pos=0;else return;}else pos++;_sigaTickerIdx[bidx]=pos;applySigaTicker(bidx);}
function sigaTickerPrev(bidx){let pos=_sigaTickerIdx[bidx]||0;if(pos>0){_sigaTickerIdx[bidx]=pos-1;applySigaTicker(bidx);}}
function goSigaTicker(i,bidx){_sigaTickerIdx[bidx]=i;applySigaTicker(bidx);if(_sigaTickerActive[bidx]){clearInterval(_sigaTickerActive[bidx]);_sigaTickerActive[bidx]=setInterval(()=>sigaTickerNext(bidx,true),3500);}}

function openSigaVtModal(bidx){
  const cd=_sigaClsData[bidx]||[];
  const br=brandResults[bidx];
  document.getElementById('vt-title').textContent='Ã‚Â«'+(br?br.brand:'')+'Ã‚Â» Ã¢â‚¬â€ SIGA Ã‚Â· Todas las Clases';
  document.getElementById('vt-sub').textContent=cd.length+' clases Ã‚Â· Solicitudes en Proceso de ConcesiÃƒÂ³n';
  document.getElementById('vt-grid').innerHTML=cd.map(item=>{
    const cls=item.hasConflict?'nok':'ok';
    let rows='';
    if(item.marks.length)rows=item.marks.map(m=>`<tr><td style="font-weight:600;color:var(--red)">${m.marca}</td><td style="font-size:10px">${m.registro}</td><td style="font-size:10px">SIGA</td></tr>`).join('');
    return`<div class="vt-class-block ${cls}"><div class="vt-class-hdr"><span class="cls-badge">CLASE ${item.cls}</span><span class="vt-cls-status ${cls}">${item.hasConflict?'Ã¢Å¡â€“ OPOSICIÃƒâ€œN':'Ã¢Å“â€ LIBRE'}</span></div>${item.marks.length?`<table class="vt-table"><thead><tr><th>DenominaciÃƒÂ³n</th><th>Exp.</th><th>Origen</th></tr></thead><tbody>${rows}</tbody></table>`:'<div class="vt-empty">Ã¢Å“â€ Sin conflictos en proceso</div>'}</div>`;
  }).join('');
  document.getElementById('vt-back').classList.add('show');
}

function renderSigaRiesgoFor(idx,rows){
  const w=document.getElementById('siga-tbl-riesgo-'+idx); if(!w)return;
  document.getElementById('siga-cnt-riesgo-'+idx).textContent=rows.length+' solicitudes';
  if(!rows.length){w.innerHTML='<div class="empty-state">Sin solicitudes en el perÃƒÂ­odo analizado para las clases seleccionadas</div>';return;}
  let h=`<table><thead><tr><th>Clase</th><th>Expediente</th><th>DenominaciÃƒÂ³n (SIGA)</th><th>Fecha Circ.</th><th>Dist.</th><th>Sim.</th><th>P.Conf</th><th>P.Conc</th><th>Criterios</th><th>Detalle</th><th>Ã‚Â¿OposiciÃƒÂ³n?</th></tr></thead><tbody>`;
  rows.forEach(r=>{
    const ok=r['hay_concesion'];
    const tag=ok?`<span class="tag-ok">Ã¢Å“â€ LIBRE</span>`:`<span class="tag-nok">Ã¢Å¡â€“ RIESGO Cl.${r['Clase']||'Ã¢â‚¬â€'}</span>`;
    const ca=r['criterios_activos']??0;
    const ct=ca===0?`<span class="tag-ok">0</span>`:ca===1?`<span class="tag-warn">1</span>`:`<span class="tag-nok">${ca}</span>`;
    h+=`<tr><td class="mono">${r['Clase']??''}</td><td class="mono" style="font-size:10px">${r['Registro']??''}</td><td style="font-weight:${ok?'400':'600'};color:${ok?'inherit':'var(--red)'}">${r['Marca']??''}</td><td style="font-size:10px;color:var(--muted)">${r['FechaCirculacion']??''}</td><td>${pctChip(r['Distancia']??0,'dist')}</td><td>${pctChip(r['Similitud']??0,'sim')}</td><td>${pctChip(r['Prob_Conf']??0,'prob')}</td><td>${pctChip(r['Prob_Conc']??0,'')}</td><td style="text-align:center">${ct}</td><td style="font-size:10px;color:var(--muted)">${r['criterios_texto']??'Ninguno'}</td><td style="text-align:center">${tag}</td></tr>`;
  });
  w.innerHTML=h+'</tbody></table>';
}

function exportSigaFor(idx,type){
  const sr=sigaResults[idx];
  if(!sr){showToast('Sin datos SIGA','info');return;}
  const br=brandResults[idx];
  const brand=(br?.brand||'marca').replace(/\s+/g,'_');
  const ts=new Date().toISOString().slice(0,10);
  let data,name;
  if(type==='riesgo'){
    data=(sr.combined||[]).map(r=>({Clase:r.Clase,Expediente:r.Registro,Denominacion:r.Marca,FechaCirculacion:r.FechaCirculacion||'',Distancia:r.Distancia,Similitud:r.Similitud,Prob_Conf:r.Prob_Conf,Prob_Conc:r.Prob_Conc,Criterios:r.criterios_activos,Detalle:r.criterios_texto,Concesion:r.hay_concesion?'SÃƒÂ':'NO'}));
    name='SIGA_Riesgo_'+brand+'_'+ts+'.xlsx';
  } else if(type==='conflicto'){
    data=sr.conflicto||[];
    name='SIGA_Conflictos_'+brand+'_'+ts+'.xlsx';
  }
  if(!data||!data.length){showToast('Sin datos para exportar','info');return;}
  const ws=XLSX.utils.json_to_sheet(data);const wb=XLSX.utils.book_new();XLSX.utils.book_append_sheet(wb,ws,type.slice(0,31));XLSX.writeFile(wb,name);
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// PROGRESS HELPERS
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function renderSteps(idx,ss){
  const ps=document.getElementById('ps-'+idx);
  if(!ps)return;
  ps.innerHTML=STEPS.map(s=>`<span class="step-pill ${ss[s.id]||'pending'}">${s.label}</span>`).join('');
}
function tickSteps(idx,ss,logText){
  STEPS.forEach(s=>{
    if(ss[s.id]==='pending'&&s.match.test(logText)){
      let m=true;
      STEPS.forEach(p=>{if(p.id===s.id)m=false;if(m&&ss[p.id]==='pending')ss[p.id]='done';});
      ss[s.id]='active';
      const pb=document.getElementById('pb-'+idx); if(pb)pb.style.width=s.pct+'%';
      const pl=document.getElementById('pl-'+idx); if(pl)pl.textContent='Procesando: '+s.label+'...';
      renderSteps(idx,ss);
    }
  });
}
function finishProg(idx,ss,hasError){
  const pw=document.getElementById('pw-'+idx),pb=document.getElementById('pb-'+idx),pl=document.getElementById('pl-'+idx);
  if(!pw)return;
  if(hasError){if(pb){pb.style.background='var(--red)';pb.style.width='100%';}if(pl)pl.textContent='Ã¢ÂÅ’ Error en el anÃƒÂ¡lisis';STEPS.forEach(s=>{if(ss[s.id]==='active')ss[s.id]='error';});}
  else{if(pb)pb.style.width='100%';if(pl)pl.textContent='Ã¢Å“â€ AnÃƒÂ¡lisis completado';STEPS.forEach(s=>{if(ss[s.id]!=='error')ss[s.id]='done';});}
  renderSteps(idx,ss);
  setTimeout(()=>{pw.style.opacity='0';pw.style.transition='opacity .5s';setTimeout(()=>pw.classList.remove('show'),500);},2000);
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// RENDER MARCA RESULTS
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function renderBrandTab(idx,brand,d){
  const expBtn=document.getElementById('exp-'+idx);
  if(expBtn)expBtn.style.display='block';
  const ompi=d.ompi_rows||[], impi=d.impi_rows||[], riesgo=d.combined||[];
  // Store raw
  if(!brandResults[idx]) brandResults[idx]={ompi,impi,riesgo:riesgo,conflicto:d.conflicto||[],file:d.file,brand,hay_concesion_global:d.hay_concesion_global};
  const br=brandResults[idx];
  // Timestamp
  const tc=document.getElementById('btab-c-'+idx);
  // Recompute with current criteria
  const rc=riesgo.map(r=>({...r,_brandNew:brand,...evalClient({...r,_brandNew:brand})}));
  const seen=new Set(),cf=[],cm={};
  rc.forEach(r=>{if(!r.hay_concesion){const k=r.Marca+'|'+r.Registro+'|'+r.Origen;if(!cm[k])cm[k]=new Set();cm[k].add(String(r.Clase));if(!seen.has(k)){seen.add(k);cf.push({Marca:r.Marca,Registro:r.Registro,Origen:r.Origen,Clases:''});}}});
  cf.forEach(it=>{const k=it.Marca+'|'+it.Registro+'|'+it.Origen;it.Clases=[...cm[k]].sort().join(', ');});
  const hay=rc.length===0||rc.every(r=>r.hay_concesion);
  br.riesgoComputed=rc; br.conflictoComputed=cf; br.hay_concesion_global=hay;

  // Show marca accordion
  const accMarca=document.getElementById('acc-marca-'+idx);
  if(accMarca)accMarca.style.display='block';
  const hint=document.getElementById('aa-hint-'+idx);
  if(hint)hint.style.display='block';

  // Fill KPIs
  const conflicts=cf.length;
  const cf4=rc.filter(r=>!r.hay_concesion&&(r.criterios_activos??0)===4).length;
  const impiEl=document.getElementById('k-impi-'+idx); if(impiEl)impiEl.textContent=impi.length;
  const cfEl=document.getElementById('k-cf-'+idx); if(cfEl)cfEl.textContent=conflicts;
  const cf4El=document.getElementById('k-cf4-'+idx); if(cf4El)cf4El.textContent=cf4;
  const riskEl=document.getElementById('k-risk-'+idx);
  if(riskEl){
    let riskText,riskClass;
    if(cf4===0){riskText='REGISTRABLE';riskClass='green';}
    else if(conflicts>0&&cf4===0){riskText='Riesgo Moderado';riskClass='orange';}
    else{riskText='EN RIESGO';riskClass='red';}
    riskEl.textContent=riskText;
    riskEl.className='kpi-num '+riskClass;
  }

  // Render conflict section (only 4/4)
  renderConflictoFor(idx,brand,cf,rc,hay);

  // Update marca accordion badge
  const badge=document.getElementById('aab-marca-'+idx);
  if(badge){badge.style.display='';badge.textContent=hay?'Ã¢Å“â€ Tu marca puede registrarse':'Ã¢Å¡Â  '+cf4+' conflicto'+(cf4!==1?'s':'')+' crÃƒÂ­tico'+(cf4!==1?'s':'');badge.style.cssText=badge.style.cssText+(hay?';background:var(--green-bg);border-color:var(--green-border);color:var(--green)':';background:var(--red-bg);border-color:var(--red-border);color:var(--red)');}

  updateStars();
}

// pctChip helper
function pctChip(val,type){
  const p=(val*100).toFixed(1)+'%';
  if(type==='sim'){if(val>=.87)return`<span class="chip chip-red">${p}</span>`;if(val>=.70)return`<span class="chip chip-orange">${p}</span>`;if(val>=.40)return`<span class="chip chip-blue">${p}</span>`;return`<span class="chip chip-green">${p}</span>`;}
  if(type==='dist'){if(val<=.30)return`<span class="chip chip-red">${p}</span>`;if(val<=.50)return`<span class="chip chip-orange">${p}</span>`;return`<span class="chip chip-green">${p}</span>`;}
  if(type==='prob'){if(val>=.50)return`<span class="chip chip-red">${p}</span>`;return`<span class="chip chip-green">${p}</span>`;}
  return`<span class="chip chip-muted">${p}</span>`;
}

function renderOmpiFor(idx,rows){
  const w=document.getElementById('tbl-ompi-'+idx); if(!w)return;
  document.getElementById('cnt-ompi-'+idx).textContent=rows.length+' registros';
  if(!rows.length){w.innerHTML='<div class="empty-state">Sin resultados OMPI</div>';return;}
  let h=`<table><thead><tr><th>Clase</th><th>N.Ã‚Â° Registro</th><th>Marca OMPI</th><th>SituaciÃƒÂ³n</th><th>Distancia</th><th>Similitud</th><th>Prob.Conf</th><th>Prob.Conc</th></tr></thead><tbody>`;
  rows.forEach(r=>{h+=`<tr><td class="mono">${r['Clase Niza']??''}</td><td class="mono">${r['N.Ã‚Â°de reg.']??''}</td><td>${r['Marca']??''}</td><td>${r['SituaciÃƒÂ³n']??''}</td><td>${pctChip(r['Distancia']??0,'dist')}</td><td>${pctChip(r['Similitud']??0,'sim')}</td><td>${pctChip(r['Prob_Conf']??0,'prob')}</td><td>${pctChip(r['Prob_Conc']??0,'')}</td></tr>`;});
  w.innerHTML=h+'</tbody></table>';
}
function renderImpiFor(idx,rows){
  const w=document.getElementById('tbl-impi-'+idx); if(!w)return;
  document.getElementById('cnt-impi-'+idx).textContent=rows.length+' registros';
  if(!rows.length){w.innerHTML='<div class="empty-state">Sin resultados IMPI</div>';return;}
  let h=`<table><thead><tr><th>Clase</th><th>Expediente</th><th>Marca Existente</th><th>Distancia</th><th>Similitud</th><th>Prob.Conf</th><th>Prob.Conc</th></tr></thead><tbody>`;
  rows.forEach(r=>{h+=`<tr><td class="mono">${r['Clase']??''}</td><td class="mono">${r['Expediente']??''}</td><td>${r['Marca_Existente']??''}</td><td>${pctChip(r['Distancia']??0,'dist')}</td><td>${pctChip(r['Similitud']??0,'sim')}</td><td>${pctChip(r['Prob_Conf']??0,'prob')}</td><td>${pctChip(r['Prob_Conc']??0,'')}</td></tr>`;});
  w.innerHTML=h+'</tbody></table>';
}
function renderRiesgoFor(idx,rows){
  const w=document.getElementById('tbl-riesgo-'+idx); if(!w)return;
  document.getElementById('cnt-riesgo-'+idx).textContent=rows.length+' registros';
  if(!rows.length){w.innerHTML='<div class="empty-state">Sin datos</div>';return;}
  let h=`<table><thead><tr><th>Origen</th><th>Clase</th><th>N.Ã‚Â°/Exp.</th><th>Marca</th><th>Dist.</th><th>Sim.</th><th>P.Conf</th><th>P.Conc</th><th>Criterios</th><th>Detalle</th><th>Ã‚Â¿ConcesiÃƒÂ³n?</th></tr></thead><tbody>`;
  rows.forEach(r=>{
    const ok=r['hay_concesion'];
    const tag=ok?`<span class="tag-ok">SÃƒÂ</span>`:`<span class="tag-nok">NO Ã‚Â· Cl.${r['Clase']||'Ã¢â‚¬â€'}</span>`;
    const ca=r['criterios_activos']??0;
    const ct=ca===0?`<span class="tag-ok">0</span>`:ca===1?`<span class="tag-warn">1</span>`:`<span class="tag-nok">${ca}</span>`;
    h+=`<tr><td class="mono" style="font-size:10px">${r['Origen']??''}</td><td class="mono">${r['Clase']??''}</td><td class="mono" style="font-size:10px">${r['Registro']??''}</td><td>${r['Marca']??''}</td><td>${pctChip(r['Distancia']??0,'dist')}</td><td>${pctChip(r['Similitud']??0,'sim')}</td><td>${pctChip(r['Prob_Conf']??0,'prob')}</td><td>${pctChip(r['Prob_Conc']??0,'')}</td><td style="text-align:center">${ct}</td><td style="font-size:10px;color:var(--muted)">${r['criterios_texto']??'Ninguno'}</td><td style="text-align:center">${tag}</td></tr>`;
  });
  w.innerHTML=h+'</tbody></table>';
}

// Ã¢â€â‚¬Ã¢â€â‚¬ Conflicto (ticker / single card) Ã¢â€â‚¬Ã¢â€â‚¬
// Only builds data for marks with 4/4 criteria
function buildClassData(conflictoRows,riesgoRows){
  const allCls=[...new Set(riesgoRows.map(r=>String(r.Clase||'')).filter(Boolean))].sort((a,b)=>Number(a)-Number(b));
  return allCls.map(cls=>{
    const cr=riesgoRows.filter(r=>String(r.Clase)===cls);
    // Only include marks with 4/4 criteria in the conflict display
    const cnf=cr.filter(r=>!r.hay_concesion&&(r.criterios_activos??0)===4);
    const anyConflict=cr.some(r=>!r.hay_concesion);
    return{cls,hasConflict:cnf.length>0,anyConflict,marks:cnf.map(r=>({marca:r.Marca||'',registro:r.Registro||'',origen:r.Origen||'',sim:r.Similitud??0,criterios:r.criterios_activos??0,criterios_txt:r.criterios_texto||''})),total:cr.length};
  });
}
function renderConflictoFor(idx,brand,rows,riesgoRows,hasConc){
  riesgoRows=riesgoRows||[];
  _classDataByBrand[idx]=buildClassData(rows,riesgoRows).sort((a,b)=>{
    const pa=a.marks.length/Math.max(a.total,1),pb=b.marks.length/Math.max(b.total,1);return pa-pb;
  });
  _tickerIdxByBrand[idx]=0;
  const cd=_classDataByBrand[idx];
  const w=document.getElementById('cf-body-'+idx); if(!w)return;
  // Count 4/4 conflicts
  const cf4Count=riesgoRows.filter(r=>!r.hay_concesion&&(r.criterios_activos??0)===4).length;
  // Status bar
  const bar=document.getElementById('cf-bar-'+idx);
  if(bar){
    bar.classList.add('show');
    const dot=document.getElementById('cgs-dot-'+idx), txt=document.getElementById('cgs-txt-'+idx), sub=document.getElementById('cgs-sub-'+idx);
    if(hasConc){
      if(dot)dot.className='cgs-dot ok';
      if(txt){txt.className='cgs-text ok';txt.textContent='Ã¢Å“â€ TU MARCA PUEDE REGISTRARSE Ã¢â‚¬â€ Ã‚Â«'+brand+'Ã‚Â»';}
      if(sub)sub.textContent='No se encontraron marcas en conflicto directo ante el IMPI';
    } else {
      const cfCls=[...new Set(cd.filter(c=>c.hasConflict).map(c=>c.cls))].join(', ');
      if(dot)dot.className='cgs-dot nok';
      if(txt){txt.className='cgs-text nok';txt.textContent='Ã¢Å¡Â  EXISTEN CONFLICTOS EN CLASE '+cfCls+' Ã¢â‚¬â€ Ã‚Â«'+brand+'Ã‚Â»';}
      if(sub)sub.textContent='Se recomienda revisiÃƒÂ³n con un abogado de marcas';
    }
  }
  const cnt=document.getElementById('cnt-cf-'+idx);
  if(cnt)cnt.textContent=cf4Count+' marca'+(cf4Count!==1?'s':'')+' con conflicto mÃƒÂ¡ximo (4/4)';
  if(!cd.length){w.innerHTML='<div class="empty-state">Sin clases analizadas</div>';return;}
  const cdWithConflicts=cd.filter(c=>c.marks.length>0);
  if(!cdWithConflicts.length){
    w.innerHTML='<div style="text-align:center;padding:32px;background:var(--green-bg);border:1px solid var(--green-border);border-radius:var(--radius-sm)"><div style="font-size:32px;margin-bottom:10px">Ã¢Å“â€</div><div style="font-size:15px;font-weight:700;color:var(--green)">Sin conflictos crÃƒÂ­ticos (4/4) ante el IMPI</div><div style="font-size:12px;color:var(--muted);margin-top:8px">No se encontraron marcas con los 4 criterios de conflicto simultÃƒÂ¡neos</div></div>';
    return;
  }
  if(cdWithConflicts.length===1){w.innerHTML='<div style="padding:16px">'+renderSingleCard(cdWithConflicts[0])+'</div>';return;}
  w.innerHTML=renderTicker(cdWithConflicts,idx);
  initTicker(idx);
}
function renderSingleCard(cd){
  const cls=cd.hasConflict?'nok':'ok';
  let h=`<div class="cls-card-single ${cls}"><div class="cls-card-hdr"><span class="cls-badge">CLASE ${cd.cls}</span><span class="cls-status ${cls}" style="font-size:12px;font-weight:600">${cd.hasConflict?'Ã¢Å¡Â  EXISTEN CONFLICTOS (4/4)':'Ã¢Å“â€ SIN CONFLICTOS CRÃƒÂTICOS'}</span></div>`;
  if(cd.marks.length){
    h+=`<table class="cls-marks-table"><thead><tr><th>Marca en Conflicto</th><th>N.Ã‚Â° Expediente</th><th>Nota</th></tr></thead><tbody>`;
    cd.marks.forEach(m=>{
      h+=`<tr><td style="font-weight:700;color:var(--red)">${m.marca}</td><td class="mono" style="font-size:10px">${m.registro}</td><td><span style="color:var(--red);font-weight:700;font-size:11px;letter-spacing:.5px">YA EXISTE</span></td></tr>`;
    });
    h+='</tbody></table>';
  } else {h+='<div style="padding:12px;font-size:12px;color:var(--green)">Ã¢Å“â€ Sin marcas con conflicto mÃƒÂ¡ximo</div>';}
  return h+'</div>';
}
function renderTicker(classArr,bidx){
  const cards=classArr.map((cd,i)=>{const cls=cd.hasConflict?'nok':'ok';return`<div class="cls-mini-card ${cls}" style="min-width:calc(33.33% - 7px)"><div class="cmc-clase">CLASE NIZA</div><div class="cmc-num">${cd.cls}</div><div class="cmc-status ${cls}">${cd.hasConflict?'Ã¢Å¡Â  '+cd.marks.length+' CONFLICTO'+(cd.marks.length!==1?'S':'')+' (4/4)':'Ã¢Å“â€ SIN CONFLICTOS'}</div><div class="cmc-count">${cd.hasConflict?cd.marks.length+' marca'+(cd.marks.length!==1?'s':'')+' con conflicto mÃƒÂ¡ximo':cd.total+' marcas analizadas'}</div></div>`}).join('');
  const dots=classArr.map((_,i)=>`<div class="t-dot${i===0?' active':''}" onclick="goTicker(${i},${bidx})"></div>`).join('');
  return`<div class="cls-ticker-wrap"><div class="cls-ticker-controls"><span class="cls-ticker-info">${classArr.length} clases con conflictos Ã‚Â· criterios 4/4</span><div class="cls-ticker-btns"><button class="btn-ticker" onclick="tickerPrev(${bidx})">Ã¢â€ Â</button><button class="btn-ticker" onclick="tickerNext(${bidx},false)">Ã¢â€ â€™</button><button class="btn-ver-todos" onclick="openVtModal(${bidx})">Ã¢ËœÂ° VER TODOS</button></div></div><div class="cls-ticker-viewport" id="tv-${bidx}"><div class="cls-ticker-track" id="tt-${bidx}">${cards}</div></div><div class="cls-ticker-dots" id="td-${bidx}">${dots}</div></div>`;
}
function initTicker(bidx){if(_activeTickerByBrand[bidx])clearInterval(_activeTickerByBrand[bidx]);_tickerIdxByBrand[bidx]=0;_activeTickerByBrand[bidx]=setInterval(()=>tickerNext(bidx,true),3500);}
function tickerVis(bidx){const vp=document.getElementById('tv-'+bidx);if(!vp)return 3;return vp.offsetWidth<600?1:vp.offsetWidth<900?2:3;}
function applyTicker(bidx){const tr=document.getElementById('tt-'+bidx),vp=document.getElementById('tv-'+bidx);if(!tr||!vp)return;const vis=tickerVis(bidx),gap=10,cw=(vp.offsetWidth-(vis-1)*gap)/vis,pos=_tickerIdxByBrand[bidx]||0;tr.style.transform=`translateX(-${pos*(cw+gap)}px)`;document.querySelectorAll(`#td-${bidx} .t-dot`).forEach((d,i)=>d.classList.toggle('active',i===pos));}
function tickerNext(bidx,auto){const cd=_classDataByBrand[bidx]||[];let pos=_tickerIdxByBrand[bidx]||0;const max=Math.max(0,cd.length-tickerVis(bidx));if(pos>=max){if(auto)pos=0;else return;}else pos++;_tickerIdxByBrand[bidx]=pos;applyTicker(bidx);}
function tickerPrev(bidx){let pos=_tickerIdxByBrand[bidx]||0;if(pos>0){_tickerIdxByBrand[bidx]=pos-1;applyTicker(bidx);}}
function goTicker(i,bidx){_tickerIdxByBrand[bidx]=i;applyTicker(bidx);if(_activeTickerByBrand[bidx]){clearInterval(_activeTickerByBrand[bidx]);_activeTickerByBrand[bidx]=setInterval(()=>tickerNext(bidx,true),3500);}}

// Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ Ver Todos Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
function openVtModal(bidx){
  const cd=_classDataByBrand[bidx]||[];
  const br=brandResults[bidx];
  document.getElementById('vt-title').textContent='Ã‚Â«'+(br?br.brand:'')+'Ã‚Â» Ã¢â‚¬â€ Todas las Clases';
  document.getElementById('vt-sub').textContent=cd.length+' clases analizadas Ã‚Â· ordenadas por riesgo Ã¢â€ â€˜';
  document.getElementById('vt-grid').innerHTML=cd.map(item=>{
    const cls=item.hasConflict?'nok':'ok';
    let rows='';
    if(item.marks.length)rows=item.marks.map(m=>`<tr><td style="font-weight:600;color:var(--red)">${m.marca}</td><td style="font-size:10px">${m.registro}</td><td style="font-size:10px">${m.origen}</td></tr>`).join('');
    return`<div class="vt-class-block ${cls}"><div class="vt-class-hdr"><span class="cls-badge">CLASE ${item.cls}</span><span class="vt-cls-status ${cls}">${item.hasConflict?'Ã¢Å“Ëœ CONFLICTOS':'Ã¢Å“â€ LIBRE'}</span></div>${item.marks.length?`<table class="vt-table"><thead><tr><th>Marca</th><th>Reg.</th><th>Origen</th></tr></thead><tbody>${rows}</tbody></table>`:'<div class="vt-empty">Ã¢Å“â€ Sin conflictos</div>'}</div>`;
  }).join('');
  document.getElementById('vt-back').classList.add('show');
}
function closeVtModal(e){if(e.target===document.getElementById('vt-back'))document.getElementById('vt-back').classList.remove('show');}
function openCritModal(){document.getElementById('crit-back').classList.add('show');}
function closeCritModal(e){if(e.target===document.getElementById('crit-back'))document.getElementById('crit-back').classList.remove('show');}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.getElementById('vt-back').classList.remove('show');document.getElementById('crit-back').classList.remove('show');}});

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// STATS / CHARTS
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
const doughnutCenter={id:'dc',afterDraw(chart){const d=chartCenterText[chart.canvas.id];if(!d||chart.config.type!=='doughnut')return;const{ctx,chartArea}=chart;if(!chartArea)return;const cx=(chartArea.left+chartArea.right)/2,cy=(chartArea.top+chartArea.bottom)/2;ctx.save();ctx.font="700 18px 'IBM Plex Mono',monospace";ctx.fillStyle='#0f1f3d';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(d.line1,cx,cy-6);ctx.font="300 9px 'IBM Plex Mono',monospace";ctx.fillStyle='#6b7a9a';ctx.fillText(String(d.line2).toUpperCase(),cx,cy+9);ctx.restore();}};
Chart.register(doughnutCenter);
function mkChart(id,cfg){if(chartInstances[id])chartInstances[id].destroy();const c=document.getElementById(id);if(!c)return null;const ch=new Chart(c.getContext('2d'),cfg);chartInstances[id]=ch;return ch;}
function setCenterLabel(id,l1,l2){chartCenterText[id]={line1:String(l1),line2:String(l2)};if(chartInstances[id])chartInstances[id].update();}

const CCC={blue:'rgba(29,106,245,.8)',purple:'rgba(109,40,217,.7)',green:'rgba(22,163,74,.8)',red:'rgba(220,38,38,.8)',orange:'rgba(217,119,6,.8)',muted:'rgba(107,122,154,.5)',grid:'rgba(221,228,240,.8)'};
const BOPTS={responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#374151',font:{family:'IBM Plex Mono',size:10},boxWidth:10}}}};

function renderStats(idx,ompi,impi,riesgo){
  const sec=document.getElementById('stats-'+idx);
  if(sec)sec.style.display='block';
  if(!riesgo.length&&!ompi.length&&!impi.length)return;
  const conflicts=riesgo.filter(r=>!r.hay_concesion).length;
  const clean=riesgo.length-conflicts;
  const pctRaw=riesgo.length?conflicts/riesgo.length*100:0;
  const pctLabel=conflicts===0?'0%':(Math.round(pctRaw)===0?'<1%':Math.round(pctRaw)+'%');

  // Criteria bar
  const buckets=[0,0,0,0,0];
  riesgo.forEach(r=>buckets[Math.min(r.criterios_activos??0,4)]++);
  mkChart('chart-crit-'+idx,{type:'bar',data:{labels:['0','1','2','3','4'],datasets:[{data:buckets,backgroundColor:[CCC.green,CCC.muted,CCC.orange,CCC.red,CCC.red],borderRadius:4}]},options:{...BOPTS,scales:{x:{ticks:{color:'#6b7a9a',font:{size:9,family:'IBM Plex Mono'}},grid:{color:CCC.grid},title:{display:true,text:'Criterios activos',color:'#6b7a9a',font:{size:9}}},y:{ticks:{color:'#6b7a9a',font:{size:9,family:'IBM Plex Mono'}},grid:{color:CCC.grid},beginAtZero:true}},plugins:{...BOPTS.plugins,legend:{display:false},tooltip:{callbacks:{label:ctx=>` ${ctx.parsed.y} marcas`}}}}});

  // Conflict doughnut Ã¢â‚¬â€ ensure visible red slice when conflicts > 0
  const minSlice=riesgo.length*0.03; // at least 3% visually
  const dispConflicts=conflicts>0?Math.max(conflicts,minSlice):0;
  const dispClean=riesgo.length-dispConflicts;
  mkChart('chart-conf-'+idx,{type:'doughnut',data:{labels:['Sin conflicto ('+clean+')','En conflicto ('+conflicts+')'],datasets:[{data:[dispClean,dispConflicts],backgroundColor:[CCC.green,CCC.red],borderColor:'#f3f6fb',borderWidth:3}]},options:{...BOPTS,cutout:'66%',plugins:{...BOPTS.plugins,tooltip:{callbacks:{label:ctx=>{const realVal=ctx.dataIndex===0?clean:conflicts;const p=riesgo.length?(realVal/riesgo.length*100).toFixed(1):0;return ' '+ctx.label+': '+p+'%';}}}}}});
  setCenterLabel('chart-conf-'+idx,pctLabel,conflicts===0?'libre':'conflictos');

  // Per-class breakdown
  const classes=[...new Set(riesgo.map(r=>String(r.Clase||'')).filter(Boolean))];
  const wrap=document.getElementById('cls-wrap-'+idx);
  if(wrap){wrap.style.display=classes.length>=2?'block':'none';}
  if(classes.length>=2) renderPerClassStats(idx,riesgo);

  // Update compare
  buildCompareTab();
}

function renderPerClassStats(idx,riesgo){
  const clsStats=[...new Set(riesgo.map(r=>String(r.Clase||'')).filter(Boolean))].map(cls=>{
    const rows=riesgo.filter(r=>String(r.Clase)===cls);
    const cf=rows.filter(r=>!r.hay_concesion);
    const pctR=rows.length?cf.length/rows.length*100:0;
    return{cls,rows,cf,pct:Math.round(pctR),pctLabel:cf.length===0?'0%':(Math.round(pctR)===0?'<1%':Math.round(pctR)+'%')};
  }).sort((a,b)=>a.pct-b.pct);
  const sub=document.getElementById('cls-btn-sub-'+idx);
  if(sub)sub.textContent='('+clsStats.length+' clases Ã‚Â· menorÃ¢â€ â€™mayor riesgo)';
  const grid=document.getElementById('cls-grid-'+idx);
  if(!grid)return;
  grid.innerHTML=clsStats.map(({cls,rows,cf,pctLabel})=>`<div class="cls-stat-card">
    <div style="font-size:10px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:4px">Clase ${cls}</div>
    <div style="font-size:11px;color:var(--muted2);margin-bottom:10px">${rows.length} marcas analizadas</div>
    <div class="cls-chart-canvas"><canvas id="cc-${idx}-${cls}"></canvas></div>
    <div class="cls-kpis">
      <div class="cls-kpi"><div class="cls-kpi-num ${cf.length?'r':'g'}">${cf.length}</div><div class="cls-kpi-lbl">Conflicto</div></div>
      <div class="cls-kpi"><div class="cls-kpi-num">${rows.length-cf.length}</div><div class="cls-kpi-lbl">Sin conflicto</div></div>
      <div class="cls-kpi"><div class="cls-kpi-num ${cf.length?'r':'g'}">${pctLabel}</div><div class="cls-kpi-lbl">% Riesgo</div></div>
    </div>
  </div>`).join('');
  clsStats.forEach(({cls,rows,cf,pctLabel})=>{
    const clean2=rows.length-cf.length;
    mkChart('cc-'+idx+'-'+cls,{type:'doughnut',data:{labels:['Libre ('+clean2+')','Conflicto ('+cf.length+')'],datasets:[{data:[clean2,cf.length],backgroundColor:[CCC.green,CCC.red],borderColor:'#f3f6fb',borderWidth:2}]},options:{...BOPTS,cutout:'66%',plugins:{...BOPTS.plugins,legend:{labels:{...BOPTS.plugins.legend.labels,font:{size:9,family:'IBM Plex Mono'},boxWidth:8}}}}});
    setCenterLabel('cc-'+idx+'-'+cls,pctLabel,cf.length===0?'libre':'conflictos');
  });
}
function toggleClsStats(idx){
  const g=document.getElementById('cls-grid-'+idx),btn=document.getElementById('cls-btn-'+idx),chev=document.getElementById('cls-btn-chev-'+idx);
  if(!g)return;
  const open=g.classList.toggle('open');
  btn.classList.toggle('open',open);
  if(chev)chev.style.transform=open?'rotate(180deg)':'';
  if(open) setTimeout(()=>{
    const classes=[...document.querySelectorAll('[id^="cc-'+idx+'-"]')].map(c=>c.id.split('-').slice(2).join('-'));
    classes.forEach(cls=>{if(chartInstances['cc-'+idx+'-'+cls])chartInstances['cc-'+idx+'-'+cls].update();});
  },100);
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// COMPARE TAB
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function buildCompareTab(){
  const brKeys=Object.keys(brandResults);
  if(!brKeys.length)return;
  const bar=document.getElementById('btabs-bar');
  const wrap=document.getElementById('brand-tabs-wrap');
  if(!wrap||wrap.style.display==='none')return;
  const existing=document.getElementById('btab-compare');
  if(existing)existing.remove();
  const tab=document.createElement('div');
  tab.className='btab compare';tab.id='btab-compare';
  tab.innerHTML='Ã°Å¸â€œÅ  ComparaciÃƒÂ³n';
  tab.onclick=switchToCompare;
  bar.appendChild(tab);
}
function buildCompareView(){
  const brKeys=Object.keys(brandResults);
  const ca=document.getElementById('compare-area');
  if(!ca)return;
  ca.style.display='block';
  ca.innerHTML=`<div class="section-label" style="margin-top:4px;margin-bottom:16px">ComparaciÃƒÂ³n EstadÃƒÂ­stica Marcaria</div>
  <div class="compare-grid">${brKeys.map(i=>{
    const br=brandResults[i];
    const riesgo=br.riesgoComputed||br.riesgo||[];
    const classes=[...new Set(riesgo.map(r=>String(r.Clase||'')).filter(Boolean))];
    const conflicts=riesgo.filter(r=>!r.hay_concesion).length;
    const pctRaw=riesgo.length?conflicts/riesgo.length*100:0;
    const pctLabel=conflicts===0?'0%':(Math.round(pctRaw)===0?'<1%':Math.round(pctRaw)+'%');
    const multiClass=classes.length>1;
    const clsRows=multiClass?[...new Set(riesgo.map(r=>String(r.Clase||'')).filter(Boolean))].map(cls=>{
      const rws=riesgo.filter(r=>String(r.Clase)===cls);
      const cf=rws.filter(r=>!r.hay_concesion).length;
      const p=rws.length?Math.round(cf/rws.length*100):0;
      return{cls,cf,total:rws.length,p};
    }).sort((a,b)=>a.p-b.p):'';
    return`<div class="cmp-card">
      <div class="cmp-brand"><span>${pctRaw===0?'Ã¢Å“â€':'Ã¢Å“Ëœ'}</span>${br.brand}</div>
      <div class="cmp-meta">${(br.ompi||[]).length} OMPI Ã‚Â· ${(br.impi||[]).length} IMPI Ã‚Â· ${classes.length} clase${classes.length!==1?'s':''}</div>
      <div style="position:relative;height:150px;margin-bottom:4px"><canvas id="cmp-c-${i}"></canvas></div>
      <div class="cmp-kpis">
        <div class="cmp-kpi"><div class="cmp-kpi-num ${pctRaw>50?'r':pctRaw>0?'':'g'}">${pctLabel}</div><div class="cmp-kpi-lbl">% Riesgo</div></div>
        <div class="cmp-kpi"><div class="cmp-kpi-num">${riesgo.length}</div><div class="cmp-kpi-lbl">Analizadas</div></div>
        <div class="cmp-kpi"><div class="cmp-kpi-num ${conflicts>0?'r':'g'}">${conflicts}</div><div class="cmp-kpi-lbl">Conflictos</div></div>
      </div>
      ${multiClass?`<button class="cmp-drill-btn" id="cmp-db-${i}" onclick="toggleDrill(${i})">Ã¢â€“Â¾ Desglose por clase (${classes.length})</button>
      <div class="cmp-drill-body" id="cmp-dd-${i}">
        ${clsRows?clsRows.map(({cls,cf,total,p})=>`<div class="cmp-cls-row"><span class="cmp-cls-badge">Cl.${cls}</span><div class="cmp-bar-wrap"><div class="cmp-bar-fill ${cf>0?'nok':'ok'}" style="width:${p}%"></div></div><span class="cmp-pct" style="color:${cf>0?'var(--red)':'var(--green)'}">${p}%</span><span class="cmp-count">${cf}/${total}</span></div>`).join(''):''}
      </div>`:''
    }
    </div>`;
  }).join('')}</div>`;
  // Render compare doughnuts
  brKeys.forEach(i=>{
    const br=brandResults[i];
    const riesgo=br.riesgoComputed||br.riesgo||[];
    const conflicts=riesgo.filter(r=>!r.hay_concesion).length;
    const clean=riesgo.length-conflicts;
    const pctRaw=riesgo.length?conflicts/riesgo.length*100:0;
    const pctLabel=conflicts===0?'0%':(Math.round(pctRaw)===0?'<1%':Math.round(pctRaw)+'%');
    const cmpMinSlice=riesgo.length*0.03;
    const cmpDispCf=conflicts>0?Math.max(conflicts,cmpMinSlice):0;
    mkChart('cmp-c-'+i,{type:'doughnut',data:{labels:['Libre ('+clean+')','Conflicto ('+conflicts+')'],datasets:[{data:[riesgo.length-cmpDispCf,cmpDispCf],backgroundColor:[CCC.green,CCC.red],borderColor:'#f3f6fb',borderWidth:2}]},options:{...BOPTS,cutout:'68%',plugins:{...BOPTS.plugins,legend:{labels:{...BOPTS.plugins.legend.labels,font:{size:9,family:'IBM Plex Mono'},boxWidth:8}},tooltip:{callbacks:{label:ctx=>{const realVal=ctx.dataIndex===0?clean:conflicts;const p=riesgo.length?(realVal/riesgo.length*100).toFixed(1):0;return ' '+ctx.label+': '+p+'%';}}}}}});
    setCenterLabel('cmp-c-'+i,pctLabel,conflicts===0?'libre':'conflictos');
  });
}
function toggleDrill(i){
  const btn=document.getElementById('cmp-db-'+i),body=document.getElementById('cmp-dd-'+i);
  if(!btn||!body)return;
  const open=body.classList.toggle('open');
  btn.classList.toggle('open',open);
  btn.innerHTML=(open?'Ã¢â€“Â´':'Ã¢â€“Â¾')+' Desglose por clase ('+body.querySelectorAll('.cmp-cls-row').length+')';
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// EXPORT
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function exportFor(idx,type){
  const br=brandResults[idx];
  if(!br){showToast('Sin datos','info');return;}
  const brand=(br.brand||'marca').replace(/\s+/g,'_');
  const ts=new Date().toISOString().slice(0,10);
  let data,name;
  if(type==='ompi'){data=br.ompi||[];name='OMPI_'+brand+'_'+ts+'.xlsx';}
  else if(type==='impi'){data=br.impi||[];name='IMPI_'+brand+'_'+ts+'.xlsx';}
  else if(type==='riesgo'){data=(br.riesgoComputed||br.riesgo||[]).map(r=>({Origen:r.Origen,Clase:r.Clase,Registro:r.Registro,Marca:r.Marca,Distancia:r.Distancia,Similitud:r.Similitud,Prob_Conf:r.Prob_Conf,Prob_Conc:r.Prob_Conc,Criterios:r.criterios_activos,Detalle:r.criterios_texto,Concesion:r.hay_concesion?'SÃƒÂ':'NO'}));name='Riesgo_'+brand+'_'+ts+'.xlsx';}
  else if(type==='conflicto'){data=br.conflictoComputed||br.conflicto||[];name='Conflictos_'+brand+'_'+ts+'.xlsx';}
  if(!data||!data.length){showToast('Sin datos para exportar','info');return;}
  const ws=XLSX.utils.json_to_sheet(data);const wb=XLSX.utils.book_new();XLSX.utils.book_append_sheet(wb,ws,type.slice(0,31));XLSX.writeFile(wb,name);
}
function downloadFor(idx){const br=brandResults[idx];if(!br||!br.file){showToast('Sin archivo generado','info');return;}window.location.href='/download?f='+encodeURIComponent(br.file);}

function exportSocial(idx){
  const data=socialResultsData[idx];
  if(!data||!Object.keys(data).length){showToast('Sin datos de redes sociales','info');return;}
  const br=brandResults[idx]||{};
  const brand=(br.brand||'marca').replace(/\s+/g,'_');
  const ts=new Date().toISOString().slice(0,10);
  const rows=Object.values(data).map(d=>({
    Plataforma:d.platform,
    Estado:d.status==='disponible_probable'?'Disponible':d.status==='ocupado'?'Ocupado':'Indeterminado',
    URL:d.url||''
  }));
  const ws=XLSX.utils.json_to_sheet(rows);const wb=XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb,ws,'Redes_Sociales');
  XLSX.writeFile(wb,'Redes_'+brand+'_'+ts+'.xlsx');
}

function exportDomain(idx){
  const data=domainResultsData[idx];
  if(!data||!data.length){showToast('Sin datos de dominios','info');return;}
  const br=brandResults[idx]||{};
  const brand=(br.brand||'marca').replace(/\s+/g,'_');
  const ts=new Date().toISOString().slice(0,10);
  const ws=XLSX.utils.json_to_sheet(data);const wb=XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb,ws,'Dominios');
  XLSX.writeFile(wb,'Dominios_'+brand+'_'+ts+'.xlsx');
}

function exportMua(idx){
  const data=muaResultsData[idx];
  if(!data||!data.length){showToast('Sin datos MUA','info');return;}
  const br=brandResults[idx]||{};
  const brand=(br.brand||'marca').replace(/\s+/g,'_');
  const ts=new Date().toISOString().slice(0,10);
  const ws=XLSX.utils.json_to_sheet(data);const wb=XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb,ws,'MUA_Empresas');
  XLSX.writeFile(wb,'MUA_'+brand+'_'+ts+'.xlsx');
}

function exportAll(idx){
  const br=brandResults[idx];
  const brand=((br?.brand)||'marca').replace(/\s+/g,'_');
  const ts=new Date().toISOString().slice(0,10);
  const wb=XLSX.utils.book_new();
  // Hoja 1 Ã¢â‚¬â€ Conflictos IMPI
  const cf=br?.conflictoComputed||br?.conflicto||[];
  if(cf.length) XLSX.utils.book_append_sheet(wb,XLSX.utils.json_to_sheet(cf),'Conflictos_IMPI');
  // Hoja 2 Ã¢â‚¬â€ Redes Sociales
  const sd=socialResultsData[idx];
  if(sd&&Object.keys(sd).length){
    const rows=Object.values(sd).map(d=>({Plataforma:d.platform,Estado:d.status==='disponible_probable'?'Disponible':d.status==='ocupado'?'Ocupado':'Indeterminado',URL:d.url||''}));
    if(rows.length) XLSX.utils.book_append_sheet(wb,XLSX.utils.json_to_sheet(rows),'Redes_Sociales');
  }
  // Hoja 3 Ã¢â‚¬â€ Dominios
  const dd=domainResultsData[idx];
  if(dd&&dd.length) XLSX.utils.book_append_sheet(wb,XLSX.utils.json_to_sheet(dd),'Dominios');
  // Hoja 4 Ã¢â‚¬â€ MUA
  const md=muaResultsData[idx];
  if(md&&md.length) XLSX.utils.book_append_sheet(wb,XLSX.utils.json_to_sheet(md),'MUA_Empresas');
  if(!wb.SheetNames.length){showToast('Sin datos para exportar','info');return;}
  XLSX.writeFile(wb,'ThinkLAB_'+brand+'_'+ts+'.xlsx');
}

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// TOAST & UTILS
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
function showToast(msg,type='warn'){
  const t=document.getElementById('toast');
  t.textContent=msg;t.className='toast '+(type==='info'?'info':'');
  t.classList.add('show');clearTimeout(_toastTimer);
  _toastTimer=setTimeout(()=>t.classList.remove('show'),3000);
}
function toggleNotaLegal(){
  const body=document.getElementById('nota-legal-body');
  const chev=document.getElementById('nota-legal-chevron');
  body.classList.toggle('open');
  chev.classList.toggle('open');
}
function iniciarNuevo(){
  if(!confirm('Ã‚Â¿Iniciar nuevo proceso? Los resultados actuales no guardados se perderÃƒÂ¡n.'))return;
  brandResults={};brandList=[''];selectedClases=[];perBrandMode=false;selectedMode='T';
  clearGiro();
  renderBrandList();renderFavGrid();
  document.querySelectorAll('.mode-btn').forEach((b,i)=>b.classList.toggle('active',i===0));
  const mw=document.getElementById('manual-wrap');if(mw)mw.classList.remove('show');
  const pw=document.getElementById('pb-wrap');if(pw)pw.innerHTML='';
  const ph=document.getElementById('pb-hint');if(ph)ph.style.display='none';
  const bpb=document.getElementById('btn-pbmode');if(bpb)bpb.classList.remove('active');
  document.getElementById('results-area').style.display='none';
  document.getElementById('compare-area').style.display='none';
  criteriaConfig={...CRITERIA_DEFAULT};criteriaMode='default';
  wizGo(1);
  showToast('Nuevo proceso iniciado','info');
}

// Init
renderBrandList(); renderFavGrid(); updateFavBadge();

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// SUPABASE AUTH
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
let _authUser = null;

function toggleAuthPanel(){
  const p = document.getElementById('auth-panel');
  if(!p) return;
  p.classList.toggle('hidden');
}

function updateAuthUI(user){
  _authUser = user;
  const btn = document.getElementById('btn-auth-toggle');
  const guest = document.getElementById('auth-guest');
  const userDiv = document.getElementById('auth-user');
  const emailEl = document.getElementById('auth-user-email');
  const msgEl = document.getElementById('auth-msg');

  if(user){
    if(btn){ btn.textContent = user.email.split('@')[0]; btn.classList.add('logged'); }
    if(guest) guest.style.display = 'none';
    if(userDiv) userDiv.style.display = 'block';
    if(emailEl) emailEl.textContent = user.email;
    if(msgEl){ msgEl.textContent = ''; msgEl.className = 'auth-msg'; }
    // Sync favorites with user account if available
    const localFavs = JSON.parse(localStorage.getItem('tim_fav') || '[]');
    if(localFavs.length) showToast('SesiÃƒÂ³n iniciada Ã¢â‚¬â€ tus marcas guardadas estÃƒÂ¡n disponibles','info');
  } else {
    if(btn){ btn.textContent = 'Iniciar SesiÃƒÂ³n'; btn.classList.remove('logged'); }
    if(guest) guest.style.display = 'block';
    if(userDiv) userDiv.style.display = 'none';
  }
}

async function registerUser(){
  if(!sbClient){ showToast('Servicio de autenticaciÃƒÂ³n no disponible'); return; }
  const email = document.getElementById('auth-email').value.trim();
  const pass  = document.getElementById('auth-password').value.trim();
  const msg   = document.getElementById('auth-msg');
  if(!email || !pass){ if(msg){msg.textContent='Completa correo y contraseÃƒÂ±a';msg.className='auth-msg err';} return; }
  if(pass.length < 6){ if(msg){msg.textContent='La contraseÃƒÂ±a debe tener al menos 6 caracteres';msg.className='auth-msg err';} return; }
  if(msg){msg.textContent='Registrando...';msg.className='auth-msg';}
  const { data, error } = await sbClient.auth.signUp({
    email, password: pass,
    options: { emailRedirectTo: window.location.origin }
  });
  if(error){
    if(msg){msg.textContent=error.message;msg.className='auth-msg err';}
    return;
  }
  if(msg){msg.textContent='Ã¢Å“â€ Registro enviado. Revisa tu correo para confirmar tu cuenta.';msg.className='auth-msg ok';}
  if(data.user) updateAuthUI(data.user);
}

async function loginUser(){
  if(!sbClient){ showToast('Servicio de autenticaciÃƒÂ³n no disponible'); return; }
  const email = document.getElementById('auth-email').value.trim();
  const pass  = document.getElementById('auth-password').value.trim();
  const msg   = document.getElementById('auth-msg');
  if(!email || !pass){ if(msg){msg.textContent='Completa correo y contraseÃƒÂ±a';msg.className='auth-msg err';} return; }
  if(msg){msg.textContent='Verificando...';msg.className='auth-msg';}
  const { data, error } = await sbClient.auth.signInWithPassword({ email, password: pass });
  if(error){
    if(msg){msg.textContent=error.message;msg.className='auth-msg err';}
    return;
  }
  updateAuthUI(data.user || null);
  // Close panel after login
  setTimeout(()=>{ const p=document.getElementById('auth-panel'); if(p)p.classList.add('hidden'); }, 800);
}

async function logoutUser(){
  if(!sbClient) return;
  await sbClient.auth.signOut();
  updateAuthUI(null);
  showToast('SesiÃƒÂ³n cerrada','info');
}

async function initAuth(){
  if(!sbClient) return;
  const { data } = await sbClient.auth.getUser();
  updateAuthUI(data.user || null);
  sbClient.auth.onAuthStateChange((_event, session) => {
    updateAuthUI(session?.user || null);
  });
}

// Close panel when clicking outside
document.addEventListener('click', e => {
  const panel = document.getElementById('auth-panel');
  const btn   = document.getElementById('btn-auth-toggle');
  if(!panel || panel.classList.contains('hidden')) return;
  if(!panel.contains(e.target) && e.target !== btn) {
    panel.classList.add('hidden');
  }
});

initAuth();

// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
// REGISTRATION GATE
// Ã¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢ÂÃ¢â€¢Â
(function(){
  const gate    = document.getElementById('reg-gate');
  const iframe  = document.getElementById('reg-iframe');
  const loading = document.getElementById('reg-loading');
  const thanks  = document.getElementById('reg-thanks');
  if(!gate || !iframe) return;

  // Usuario ya registrado Ã¢â€ â€™ quitar gate inmediatamente
  if(localStorage.getItem('tim_registered') === '1'){
    gate.classList.add('done');
    return;
  }

  // Bloquear scroll del fondo mientras el gate estÃƒÂ¡ activo
  document.body.style.overflow = 'hidden';

  // Bloquear tecla Escape para que no pueda esquivar el modal
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape' && localStorage.getItem('tim_registered') !== '1'){
      e.preventDefault();
      e.stopPropagation();
    }
  }, true);

  let loadCount = 0;
  iframe.addEventListener('load', function(){
    loadCount++;
    if(loadCount === 1){
      // Primera carga: formulario listo Ã¢â€ â€™ ocultar spinner
      loading.classList.add('hidden');
    } else {
      // Segunda carga: usuario enviÃƒÂ³ el formulario Ã¢â€ â€™ mostrar gracias
      iframe.style.display = 'none';
      thanks.classList.add('show');
    }
  });
})();

function enterApp(){
  localStorage.setItem('tim_registered', '1');
  const gate = document.getElementById('reg-gate');
  if(gate){
    gate.style.transition = 'opacity .45s';
    gate.style.opacity = '0';
    setTimeout(()=>{ gate.classList.add('done'); gate.style.opacity = ''; }, 450);
  }
  document.body.style.overflow = '';
}

</script>
</body>
</html>
"""

# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/stream")
def stream():
    brand       = request.args.get("brand", "").strip()
    mode        = request.args.get("mode", "T").upper()
    classes_raw = request.args.get("classes_raw", "")
    skip_ompi   = request.args.get("skip_ompi", "false").lower() == "true"
    skip_impi   = request.args.get("skip_impi", "false").lower() == "true"
    headed      = request.args.get("headed", "false").lower() == "true"

    q = queue.Queue()

    def run():
        script_dir = Path(__file__).parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))

        orig_out, orig_err = sys.stdout, sys.stderr
        sys.stdout = StreamCapture(q, orig_out)
        sys.stderr = StreamCapture(q, orig_err)

        out_file  = None
        error     = None
        ompi_enriched = []
        impi_rows = []
        combined  = []
        conflicto = []
        hay_concesion_global = True

        try:
            from ORCH_ONE import (
                train_model, scrape_ompi, scrape_impi,
                build_excel, compute_metrics, evaluar_criterios
            )

            classes = parse_classes(mode, classes_raw)
            q.put(("log", f"  Clases Ã¢â€ â€™ {classes}"))

            q.put(("log", "Ã°Å¸â€Â§ Entrenando modelo de similitud..."))
            model = train_model(1000)
            q.put(("log", "Ã¢Å“â€¦ Modelo listo."))

            ompi_rows_raw = []
            if not skip_ompi:
                q.put(("log", "Ã°Å¸Å’Â Iniciando scraping OMPI / Madrid Monitor..."))
                try:
                    ompi_rows_raw = scrape_ompi(brand, classes, headless=not headed)
                    q.put(("log", f"   Ã¢â€ â€™ {len(ompi_rows_raw)} registros OMPI encontrados."))
                except Exception as e:
                    q.put(("log", f"Ã¢Å¡Â Ã¯Â¸Â  Error OMPI: {e}"))
            else:
                q.put(("log", "Ã¢ÂÂ­  OMPI omitida por configuraciÃƒÂ³n."))

            for r in ompi_rows_raw:
                metrics = compute_metrics(brand, r["Marca"], model)
                ompi_enriched.append({**r, **metrics})

            if not skip_impi:
                q.put(("log", "Ã°Å¸Å’Â Iniciando scraping IMPI / Marcanet..."))
                impi_rows = scrape_impi(brand, classes, model)
                q.put(("log", f"   Ã¢â€ â€™ {len(impi_rows)} registros IMPI encontrados."))
            else:
                q.put(("log", "Ã¢ÂÂ­  IMPI omitida por configuraciÃƒÂ³n."))

            # Construir combined + anÃƒÂ¡lisis de riesgo
            for r in ompi_enriched:
                ev = evaluar_criterios(
                    r.get("Distancia", 0), r.get("Similitud", 0),
                    r.get("Prob_Conf", 0), r.get("Prob_Conc", 0)
                )
                combined.append({
                    "Origen": "OMPI", "Clase": r.get("Clase Niza", ""),
                    "Registro": r.get("N.Ã‚Â°de reg.", ""), "Marca": r.get("Marca", ""),
                    "Distancia": r.get("Distancia", 0), "Similitud": r.get("Similitud", 0),
                    "Prob_Conf": r.get("Prob_Conf", 0), "Prob_Conc": r.get("Prob_Conc", 0),
                    **ev
                })
            for r in impi_rows:
                ev = evaluar_criterios(
                    r.get("Distancia", 0), r.get("Similitud", 0),
                    r.get("Prob_Conf", 0), r.get("Prob_Conc", 0)
                )
                combined.append({
                    "Origen": "IMPI", "Clase": r.get("Clase", ""),
                    "Registro": r.get("Expediente", ""), "Marca": r.get("Marca_Existente", ""),
                    "Distancia": r.get("Distancia", 0), "Similitud": r.get("Similitud", 0),
                    "Prob_Conf": r.get("Prob_Conf", 0), "Prob_Conc": r.get("Prob_Conc", 0),
                    **ev
                })
            combined.sort(key=lambda x: x["Similitud"], reverse=True)

            # Marcas en conflicto
            from collections import defaultdict
            clases_por_marca = defaultdict(set)
            seen_keys = set()
            for r in combined:
                if not r["hay_concesion"]:
                    key = (r["Marca"], r["Registro"], r["Origen"])
                    clases_por_marca[key].add(str(r["Clase"]))
                    if key not in seen_keys:
                        seen_keys.add(key)
                        conflicto.append({
                            "Marca": r["Marca"],
                            "Registro": r["Registro"],
                            "Origen": r["Origen"],
                            "Clases": ""
                        })
            for item in conflicto:
                key = (item["Marca"], item["Registro"], item["Origen"])
                item["Clases"] = ", ".join(sorted(clases_por_marca[key]))

            hay_concesion_global = all(r["hay_concesion"] for r in combined) if combined else True

            # Generar Excel
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_dir = Path(__file__).parent / "outputs"
            out_dir.mkdir(exist_ok=True)
            out_file = str(out_dir / f"analisis_{brand.replace(' ','_')}_{ts}.xlsx")
            q.put(("log", "Ã°Å¸â€œÅ  Generando Excel completo..."))
            build_excel(brand, ompi_rows_raw, impi_rows, out_file, model)
            q.put(("log", f"Ã¢Å“â€¦ Archivo guardado: {Path(out_file).name}"))

        except Exception as e:
            import traceback
            error = str(e)
            q.put(("log", f"Ã¢ÂÅ’ Error crÃƒÂ­tico: {e}"))
            q.put(("log", traceback.format_exc()))
        finally:
            sys.stdout = orig_out
            sys.stderr = orig_err
            q.put(("done", json.dumps({
                "file": out_file,
                "ompi_rows": ompi_enriched,
                "impi_rows": impi_rows,
                "combined": combined,
                "conflicto": conflicto,
                "hay_concesion_global": hay_concesion_global,
                "error": error,
            }, ensure_ascii=False, default=str)))

    threading.Thread(target=run, daemon=True).start()

    def generate():
        while True:
            try:
                etype, data = q.get(timeout=600)
                yield f"event: {etype}\ndata: {data}\n\n"
                if etype == "done":
                    break
            except queue.Empty:
                yield "event: log\ndata: Ã¢Å¡Â Ã¯Â¸Â  Timeout esperando respuesta.\n\n"
                break

    return Response(
        generate(), mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@app.route("/download")
def download():
    f = request.args.get("f", "")
    p = Path(f)
    if not p.exists() or not f.endswith(".xlsx"):
        return "Archivo no encontrado.", 404
    return send_file(str(p), as_attachment=True, download_name=p.name)


# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ showExtraTools trigger Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
# Called from JS after brand analysis completes.
# (No backend needed Ã¢â‚¬â€ JS handles it via renderBrandResults hook)

# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ Social media availability check Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
@app.route("/social_check")
def social_check():
    username_raw = request.args.get("username", "").strip()
    import re as _re, time as _time, requests as _req
    from urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter

    username = _re.sub(r"[^a-z0-9._]+", "", username_raw.lower())

    PLATFORMS = {
        "github":      "https://api.github.com/users/{u}",
        "instagram":   "https://www.instagram.com/{u}/",
        "tiktok":      "https://www.tiktok.com/@{u}",
        "youtube":     "https://www.youtube.com/@{u}",
        "pinterest":   "https://www.pinterest.com/{u}/",
        "twitter_x":   "https://twitter.com/{u}",
        "linkedin":    "https://www.linkedin.com/company/{u}",
        "threads":     "https://www.threads.net/@{u}",
        "snapchat":    "https://www.snapchat.com/add/{u}",
        "twitch":      "https://www.twitch.tv/{u}",
        "telegram":    "https://t.me/{u}",
        "patreon":     "https://www.patreon.com/{u}",
        "substack":    "https://{u}.substack.com",
        "vimeo":       "https://vimeo.com/{u}",
        "spotify":     "https://open.spotify.com/user/{u}",
        "devto":       "https://dev.to/{u}",
        "mixcloud":    "https://www.mixcloud.com/{u}/",
        "strava":      "https://www.strava.com/athletes/{u}",
        "discord":     "https://discord.gg/{u}",
        "whatsapp":    "https://whatsapp.com/channel/{u}",
        "line":        "https://line.me/ti/p/~{u}",
        "meetup":      "https://www.meetup.com/members/{u}/",
        "goodreads":   "https://www.goodreads.com/{u}",
        "houzz":       "https://www.houzz.com/user/{u}",
        "viber":       "https://chats.viber.com/{u}",
    }

    HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}
    TIMEOUT = 10

    def check_url(url, platform):
        try:
            if platform == "github":
                r = _req.get(url, headers=HDR, timeout=TIMEOUT)
                if r.status_code == 200: return "ocupado", url
                if r.status_code == 404: return "disponible_probable", url
                return "indeterminado", url
            r = _req.head(url, headers=HDR, timeout=TIMEOUT, allow_redirects=True)
            code = r.status_code
            if code in (405, 400): r = _req.get(url, headers=HDR, timeout=TIMEOUT, allow_redirects=True); code = r.status_code
            if code == 200: return "ocupado", url
            if code == 404: return "disponible_probable", url
            return "indeterminado", url
        except Exception: return "indeterminado", url

    def generate():
        import json as _json
        for platform, pattern in PLATFORMS.items():
            url = pattern.replace("{u}", username)
            status, checked_url = check_url(url, platform)
            data = _json.dumps({"platform": platform, "status": status, "url": checked_url})
            yield "event: progress\ndata: " + data + "\n\n"
            _time.sleep(0.3)
        yield "event: done\ndata: ok\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ Domain availability check (static common TLDs) Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
@app.route("/domain_check")
def domain_check():
    term = request.args.get("term", "").strip().lower()
    import re as _re, socket as _socket, json as _json, time as _t
    term_clean = _re.sub(r"[^a-z0-9-]", "", term)
    if not term_clean:
        def gen_empty():
            yield "event: result\ndata: []\n\n"
            yield "event: done\ndata: ok\n\n"
        return Response(gen_empty(), mimetype="text/event-stream")

    TLDS = [".com", ".mx", ".com.mx", ".net", ".org", ".io", ".co",
            ".app", ".store", ".shop", ".digital", ".tech", ".brand",
            ".online", ".site", ".info", ".biz", ".lat"]

    def check_domain(domain):
        """
        Dual-method domain availability check:
        1. DNS lookup  Ã¢â‚¬â€ if resolves Ã¢â€ â€™ registered (most reliable signal)
        2. HTTP HEAD   Ã¢â‚¬â€ if 200 or parking-page pattern Ã¢â€ â€™ registered
        Fallback rule: prefer "No disponible" when uncertain (avoid false positives).
        """
        import requests as _req

        # Ã¢â€â‚¬Ã¢â€â‚¬ Method 1: DNS resolution Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
        dns_resolved = False
        dns_nxdomain  = False
        try:
            _socket.getaddrinfo(domain, None, _socket.AF_UNSPEC, _socket.SOCK_STREAM)
            dns_resolved = True  # domain has DNS records Ã¢â€ â€™ registered
        except _socket.gaierror as e:
            msg = str(e.args[1]).lower() if len(e.args) > 1 else ""
            # NXDOMAIN signals: "name or service not known", "non-existent domain"
            if any(kw in msg for kw in ("not known", "nxdomain", "non-existent",
                                         "does not exist", "no such host")):
                dns_nxdomain = True
        except Exception:
            pass

        if dns_resolved:
            return {"Dominio": domain, "Estado": "No disponible"}

        # Ã¢â€â‚¬Ã¢â€â‚¬ Method 2: HTTP check (catches registered domains with parking pages) Ã¢â€â‚¬Ã¢â€â‚¬
        # Registered domains often resolve via registrar nameservers even when
        # the domain itself has no A-record for the www hostname.
        # A 200 response Ã¢â€ â€™ active server Ã¢â€ â€™ definitely registered.
        # Connection refused / timeout Ã¢â€ â€™ could be either; use as secondary signal.
        http_status = None
        try:
            HDR = {"User-Agent": "Mozilla/5.0 (compatible; TIM-checker/1.0)"}
            r = _req.head(f"https://{domain}", headers=HDR, timeout=6,
                          allow_redirects=True)
            http_status = r.status_code
        except _req.exceptions.ConnectionError:
            http_status = "conn_refused"
        except _req.exceptions.Timeout:
            http_status = "timeout"
        except Exception:
            http_status = "error"

        if http_status == 200:
            return {"Dominio": domain, "Estado": "No disponible"}

        # Ã¢â€â‚¬Ã¢â€â‚¬ Decision logic Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
        # dns_nxdomain = strong signal of availability
        # conn_refused / timeout with no DNS = probably available
        # any other http error = treat as indeterminate
        if dns_nxdomain or http_status in ("conn_refused", "timeout", "error"):
            return {"Dominio": domain, "Estado": "Posible disponible"}

        return {"Dominio": domain, "Estado": "Indeterminado"}

    def generate():
        rows = []
        for tld in TLDS:
            domain = term_clean + tld
            row = check_domain(domain)
            rows.append(row)
            _t.sleep(0.05)   # DNS is much faster than HTTP Ã¢â‚¬â€ short pause only
        yield "event: result\ndata: " + _json.dumps(rows, ensure_ascii=False) + "\n\n"
        yield "event: done\ndata: ok\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ MUA business name check Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
@app.route("/mua_check")
def mua_check():
    term = request.args.get("term", "").strip()
    import json as _json, time as _t

    def generate():
        yield 'event: progress\ndata: ' + _json.dumps({'pct':10,'msg':'Iniciando navegador...'}) + '\n\n'
        _t.sleep(0.5)
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            yield 'event: progress\ndata: ' + _json.dumps({'pct':25,'msg':'Abriendo SIEM MUA...'}) + '\n\n'

            options = ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--log-level=3")
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(60)

            URL = "https://mua.economia.gob.mx/mua-web/showAutorizadasHome"
            driver.get(URL)

            yield 'event: progress\ndata: ' + _json.dumps({'pct':50,'msg':'Buscando denominaciÃƒÂ³n...'}) + '\n\n'

            wait = WebDriverWait(driver, 25)
            campo = wait.until(EC.element_to_be_clickable((By.ID, "razonSocial")))
            campo.clear(); campo.send_keys(term)
            boton = wait.until(EC.element_to_be_clickable((By.ID, "btnConsultarDoRS")))
            boton.click()
            _t.sleep(3)

            yield 'event: progress\ndata: ' + _json.dumps({'pct':80,'msg':'Extrayendo resultados...'}) + '\n\n'

            rows = []
            try:
                tabla = wait.until(EC.presence_of_element_located((By.ID, "idTblDenominaciones")))
                _t.sleep(2)
                hdrs = [th.text.strip() or f"Col{i+1}" for i, th in enumerate(tabla.find_elements(By.CSS_SELECTOR, "thead th"))]
                filas = tabla.find_elements(By.CSS_SELECTOR, "tbody tr")
                for fila in filas:
                    celdas = fila.find_elements(By.TAG_NAME, "td")
                    if not celdas: continue
                    row = {}
                    for i, cel in enumerate(celdas):
                        key = hdrs[i] if i < len(hdrs) else f"Col{i+1}"
                        row[key] = cel.text.strip()
                    if any(v for v in row.values()):
                        rows.append(row)
                # Filter out "no hay datos" rows
                if rows and "no hay datos disponibles" in str(rows).lower():
                    rows = []
            except Exception as e:
                pass
            finally:
                driver.quit()

            yield "event: result\ndata: " + _json.dumps(rows, ensure_ascii=False) + "\n\n"

        except ImportError:
            yield "event: result\ndata: " + _json.dumps([{'Error':'Selenium no instalado. Ejecuta: pip install selenium'}]) + "\n\n"
        except Exception as e:
            yield "event: result\ndata: " + _json.dumps([{'Error':str(e)}]) + "\n\n"

        yield "event: done\ndata: ok\n\n"

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬ SIGA Ã¢â‚¬â€ Rastreo de OposiciÃƒÂ³n / Gaceta Marcaria Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬Ã¢â€â‚¬
@app.route("/siga_scan")
def siga_scan():
    brand       = request.args.get("brand", "").strip()
    mode        = request.args.get("mode", "T").upper()
    classes_raw = request.args.get("classes_raw", "")

    if not brand:
        def _empty():
            yield 'event: done\ndata: ' + json.dumps({"error": "Marca no especificada"}) + '\n\n'
        return Response(_empty(), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    q = queue.Queue()

    def run():
        error    = None
        combined = []
        conflicto = []
        hay_concesion_global = True
        fecha_min = ""
        fecha_max = ""
        total_registros = 0

        try:
            script_dir = Path(__file__).parent
            if str(script_dir) not in sys.path:
                sys.path.insert(0, str(script_dir))

            from SIGA_MONITOR import scrape_siga
            from ORCH_ONE import train_model, compute_metrics, evaluar_criterios

            classes = parse_classes(mode, classes_raw)
            q.put(("log", f"Ã°Å¸â€œâ€¹ SIGA: Marca Ã¢â€ â€™ Ã‚Â«{brand}Ã‚Â» Ã‚Â· Clases Niza Ã¢â€ â€™ {classes}"))

            q.put(("log", "Ã°Å¸â€Â§ SIGA: Entrenando modelo de similitud..."))
            model = train_model(1000)
            q.put(("log", "Ã¢Å“â€¦ SIGA: Modelo listo."))

            # Scrape SIGA
            registros = scrape_siga(
                classes     = classes,
                headless    = True,
                dias_atras  = 60,
                progress_cb = lambda msg: q.put(("log", msg)),
            )

            total_registros = len(registros)
            q.put(("log", f"Ã°Å¸â€œâ€¹ SIGA: {total_registros} registros obtenidos. Aplicando anÃƒÂ¡lisis ML..."))

            # Compute date range from Fecha CirculaciÃƒÂ³n
            fechas_raw = [r.get("Fecha CirculaciÃƒÂ³n", "") for r in registros
                          if r.get("Fecha CirculaciÃƒÂ³n") and r.get("Fecha CirculaciÃƒÂ³n") != "N/A"]
            if fechas_raw:
                fechas_sorted = sorted(set(fechas_raw))
                fecha_min = fechas_sorted[0]
                fecha_max = fechas_sorted[-1]

            # Apply ML metrics + criteria evaluation
            for r in registros:
                marca_siga = r.get("DenominaciÃƒÂ³n", "").strip()
                if not marca_siga:
                    continue
                try:
                    metrics = compute_metrics(brand, marca_siga, model)
                    ev      = evaluar_criterios(
                        metrics.get("Distancia", 0), metrics.get("Similitud", 0),
                        metrics.get("Prob_Conf", 0), metrics.get("Prob_Conc", 0)
                    )
                    combined.append({
                        "Origen":            "SIGA",
                        "Clase":             r.get("Clase", ""),
                        "Registro":          r.get("Expediente", ""),
                        "Marca":             marca_siga,
                        "FechaCirculacion":  r.get("Fecha CirculaciÃƒÂ³n", ""),
                        "FechaPresentacion": r.get("Fecha PresentaciÃƒÂ³n", ""),
                        "Gaceta":            r.get("Gaceta", ""),
                        "Distancia":         metrics.get("Distancia", 0),
                        "Similitud":         metrics.get("Similitud", 0),
                        "Prob_Conf":         metrics.get("Prob_Conf", 0),
                        "Prob_Conc":         metrics.get("Prob_Conc", 0),
                        **ev,
                    })
                except Exception:
                    continue

            combined.sort(key=lambda x: x.get("Similitud", 0), reverse=True)

            # Build conflict list
            from collections import defaultdict
            clases_por_marca = defaultdict(set)
            seen_keys = set()
            for r in combined:
                if not r.get("hay_concesion", True):
                    key = (r["Marca"], r["Registro"], "SIGA")
                    clases_por_marca[key].add(str(r["Clase"]))
                    if key not in seen_keys:
                        seen_keys.add(key)
                        conflicto.append({
                            "Marca":    r["Marca"],
                            "Registro": r["Registro"],
                            "Origen":   "SIGA",
                            "Clases":   "",
                        })
            for item in conflicto:
                key = (item["Marca"], item["Registro"], "SIGA")
                item["Clases"] = ", ".join(sorted(clases_por_marca[key]))

            hay_concesion_global = (
                all(r.get("hay_concesion", True) for r in combined)
                if combined else True
            )

            q.put(("log", f"Ã¢Å“â€¦ SIGA: AnÃƒÂ¡lisis completo Ã¢â‚¬â€ {len(conflicto)} posibles conflictos detectados."))

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            e_type = type(e).__name__
            # Selenium exceptions embed a full ChromeDriver stacktrace after "Stacktrace:" Ã¢â‚¬â€ strip it
            raw_msg = str(e).strip()
            e_msg = raw_msg.split("Stacktrace:")[0].strip()
            e_msg = e_msg.removeprefix("Message:").strip() or None
            error = f"{e_type}: {e_msg}" if e_msg else e_type
            q.put(("log", f"Ã¢ÂÅ’ SIGA Error ({e_type}): {e_msg or '(sin mensaje)'}"))
            q.put(("log", tb))
        finally:
            q.put(("done", json.dumps({
                "combined":            combined,
                "conflicto":           conflicto,
                "hay_concesion_global": hay_concesion_global,
                "fecha_min":           fecha_min,
                "fecha_max":           fecha_max,
                "total_registros":     total_registros,
                "dias_atras":          60,
                "error":               error,
            }, ensure_ascii=False, default=str)))

    threading.Thread(target=run, daemon=True).start()

    def generate():
        while True:
            try:
                etype, data = q.get(timeout=900)   # 15-min timeout for SIGA
                yield f"event: {etype}\ndata: {data}\n\n"
                if etype == "done":
                    break
            except queue.Empty:
                yield "event: log\ndata: Ã¢Å¡Â Ã¯Â¸Â SIGA: Timeout.\n\n"
                break

    return Response(
        generate(), mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


if __name__ == "__main__":
    print("=" * 55)
    print("  Trademark Insights MÃƒÂ©xico Ã¢â‚¬â€ powered by markum")
    print("  Abre en tu navegador: http://localhost:5050")
    print("=" * 55)
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)