#!/usr/bin/env python3
"""Assembles gitguild/index.html from gitguild/src/* sources."""
import os, re, base64

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(ROOT, "gitguild", "src")
ASSETS_DIR = os.path.join(ROOT, "gitguild", "assets")
INDEX_HTML = os.path.join(ROOT, "gitguild", "index.html")

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    template_path = os.path.join(SRC_DIR, "template.html")
    styles_path = os.path.join(SRC_DIR, "styles.css")
    geom_path = os.path.join(SRC_DIR, "emblem-geometry.js")
    projects_path = os.path.join(SRC_DIR, "projects.js")
    app_path = os.path.join(SRC_DIR, "app.js")
    favicon_path = os.path.join(ASSETS_DIR, "favicon.svg")
    vendor_dir = os.path.join(SRC_DIR, "vendor")
    react_path = os.path.join(vendor_dir, "react.production.min.js")
    react_dom_path = os.path.join(vendor_dir, "react-dom.production.min.js")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Missing template: {template_path}")

    template = read_file(template_path)
    styles = read_file(styles_path) if os.path.exists(styles_path) else ""
    geom = read_file(geom_path) if os.path.exists(geom_path) else ""
    projects = read_file(projects_path) if os.path.exists(projects_path) else ""
    app = read_file(app_path) if os.path.exists(app_path) else ""
    react = read_file(react_path) if os.path.exists(react_path) else ""
    react_dom = read_file(react_dom_path) if os.path.exists(react_dom_path) else ""

    # Favicon base64
    if os.path.exists(favicon_path):
        fav_content = read_file(favicon_path)
        fav_b64 = base64.b64encode(fav_content.encode("utf-8")).decode("ascii")
        favicon_uri = f"data:image/svg+xml;base64,{fav_b64}"
    else:
        favicon_uri = "data:image/svg+xml;utf8,<svg></svg>"

    # Mark symbol
    mark_symbol = """<svg style="display:none" aria-hidden="true">
  <symbol id="guild-mark" viewBox="465.5 81.8 476.0 476.0">
    <g fill="none" stroke="#EBE8DB" stroke-width="9.6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M703.8,209.7L703.6,483.9"/>
      <path d="M701.7,319.7L648.1,276.1"/>
      <path d="M853.5,217.3L720.6,144.3"/>
      <path d="M705.7,409.7C713.5,404.8 742.1,389.4 752.7,380.3C763.3,371.2 766.5,359.5 769.3,355.3"/>
      <path d="M685.3,498.0L552.5,423.2"/>
      <path d="M721.5,498.4L854.4,423.3"/>
    </g>
    <g fill="none" stroke="#F4A330" stroke-width="9.6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M577.7,253.7C577.1,258.5 573.1,273.7 574.3,282.3C575.5,290.9 582.9,301.5 584.7,305.4"/>
      <path d="M582.6,331.1C581.3,334.3 576.4,343.6 574.7,350.7C573.0,357.8 572.7,369.9 572.3,373.7"/>
      <path d="M744.0,193.7C744.3,194.5 733.6,190.5 745.7,198.3C757.8,206.1 804.9,233.3 816.7,240.3"/>
      <path d="M615.6,318.9C619.8,322.0 633.1,317.3 640.7,337.7C648.3,358.1 654.6,421.2 661.0,441.3C667.4,461.4 676.0,455.5 679.0,458.3"/>
      <path d="M553.7,217.7C570.2,208.4 634.4,171.4 652.7,161.7C671.0,152.0 657.7,162.2 663.3,159.3C668.9,156.4 682.6,147.0 686.5,144.5"/>
      <path d="M538.2,393.1L538.5,337.9"/>
      <path d="M538.5,246.2L538.0,300.7"/>
      <path d="M766.9,277.7C767.2,286.1 769.0,316.1 768.7,328.0C768.4,339.9 765.9,345.5 765.3,349.0"/>
      <path d="M592.0,404.3C601.5,410.0 637.3,432.1 648.7,438.3C660.2,444.5 658.7,441.1 660.7,441.7"/>
      <path d="M872.8,301.2C872.3,299.4 870.2,299.9 869.7,290.7C869.2,281.5 869.7,253.5 869.7,246.1"/>
      <path d="M728.0,459.3C728.8,458.2 718.9,461.2 732.7,452.7C746.5,444.2 795.3,418.9 810.7,408.3C826.1,397.7 822.9,392.2 825.3,389.0"/>
      <path d="M834.7,341.0C834.5,345.8 834.4,362.0 833.3,370.0C832.2,378.0 824.7,383.6 828.0,389.0C831.3,394.4 848.9,400.3 853.0,402.5"/>
      <path d="M869.7,338.0L869.5,393.3"/>
      <path d="M769.0,326.7C774.7,323.2 794.1,316.5 803.3,305.7C812.5,294.9 816.2,273.5 824.3,261.7C832.4,249.9 847.5,239.6 852.2,235.2"/>
      <path d="M577.7,253.7C580.5,250.8 580.9,245.6 594.7,236.3C608.5,227.0 648.8,210.3 660.3,197.7C671.8,185.1 663.1,166.9 663.7,160.7"/>
      <path d="M602.4,337.1C603.0,340.9 606.6,353.7 606.3,360.0C606.0,366.3 609.0,367.6 600.3,374.7C591.6,381.8 561.9,398.0 554.2,402.7"/>
    </g>
    <circle cx="703.5" cy="137.0" r="15.75" fill="none" stroke="#EBE8DB" stroke-width="9.5"/>
    <circle cx="703.5" cy="191.1" r="15.75" fill="none" stroke="#EBE8DB" stroke-width="9.5"/>
    <circle cx="538.0" cy="227.6" r="15.75" fill="none" stroke="#F4A330" stroke-width="9.5"/>
    <circle cx="869.1" cy="227.5" r="15.75" fill="none" stroke="#F4A330" stroke-width="9.5"/>
    <circle cx="640.6" cy="259.1" r="15.75" fill="none" stroke="#EBE8DB" stroke-width="9.5"/>
    <circle cx="766.6" cy="259.1" r="15.75" fill="none" stroke="#F4A330" stroke-width="9.5"/>
    <circle cx="538.1" cy="319.3" r="15.75" fill="none" stroke="#F4A330" stroke-width="9.5"/>
    <circle cx="597.0" cy="319.3" r="15.75" fill="none" stroke="#F4A330" stroke-width="9.5"/>
    <circle cx="869.1" cy="319.4" r="15.75" fill="none" stroke="#F4A330" stroke-width="9.5"/>
    <circle cx="537.9" cy="411.7" r="15.75" fill="none" stroke="#F4A330" stroke-width="9.5"/>
    <circle cx="869.1" cy="411.9" r="15.75" fill="none" stroke="#F4A330" stroke-width="9.5"/>
    <circle cx="703.4" cy="502.5" r="15.75" fill="none" stroke="#EBE8DB" stroke-width="9.5"/>
  </symbol>
</svg>"""

    # ADR-0003 step 4: lede slot reads collective.lede (90-120 chars, placeholder).
    mlede = re.search(r"lede:\s*'([^']+)'", projects)
    lede = mlede.group(1) if mlede else ""
    if not mlede:
        print("WARNING: collective.lede not found in projects.js; using empty lede")
    elif not (90 <= len(lede) <= 120):
        print(f"WARNING: lede slot is {len(lede)} chars (want 90-120): {lede[:60]}...")
    github_link = "https://github.com/Git-Guild"
    mail_link = "mailto:hello@gitguild.dev"
    quickstart_cmd = "npx @gitguild/cli open <project>"

    # ADR-0003 step 1: the chat CTA reads collective.links.chat (single source).
    m = re.search(r"chat:\s*'([^']+)'", projects)
    if m:
        chat_link = m.group(1)
    else:
        chat_link = "https://discord.com/"
        print("WARNING: collective.links.chat not found in projects.js; using bare fallback")

    # Placeholder-link guard (warn only; qa_assert.py fails until these are real).
    if chat_link.rstrip("/") in ("https://discord.com", "https://discord.gg"):
        print(f"WARNING: placeholder chat link ({chat_link}) TODO(chat-link) — replace with the real invite")
    bare_projects = sorted(set(re.findall(r"(?:url|repo|docs):\s*'(https://github\.com/)'", projects)))
    if bare_projects:
        n = len(re.findall(r"(?:url|repo|docs):\s*'https://github\.com/'", projects))
        print(f"WARNING: {n} bare project URL placeholder(s) ({', '.join(bare_projects)}) — replace with real links")

    # Replace placeholders
    html = template
    html = html.replace("__FAVICON__", favicon_uri)
    html = html.replace("__STYLES__", styles)
    html = html.replace("__MARK_SYMBOL__", mark_symbol)
    html = html.replace("__VIEW__", "465.5 81.8 476.0 476.0")
    html = html.replace("__LEDE__", lede)
    html = html.replace("__GITHUB__", github_link)
    html = html.replace("__CHAT__", chat_link)
    html = html.replace("__MAIL__", mail_link)
    html = html.replace("__QUICKSTART__", quickstart_cmd)
    html = html.replace("__PROJECTS__", projects)
    html = html.replace("__GEOMETRY__", geom)
    html = html.replace("__REACT__", react)
    html = html.replace("__REACT_DOM__", react_dom)
    html = html.replace("__APP__", app)

    with open(INDEX_HTML, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    print(f"Successfully assembled {INDEX_HTML}")

if __name__ == "__main__":
    main()
