#!/usr/bin/env python3
"""Assembles gitguild/index.html from gitguild/src/* sources."""
import os, re, base64, json, sys, html
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.join(ROOT, "gitguild", "src")
ASSETS_DIR = os.path.join(ROOT, "gitguild", "assets")
INDEX_HTML = os.path.join(ROOT, "gitguild", "index.html")
SNAPSHOT_PATH = os.path.join(ROOT, "data", "github-projects.json")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from project_catalog import build_catalog, slugify

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_script_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")) \
        .replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

def date_label(value):
    if not value:
        return "Not provided"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y")
    except (AttributeError, ValueError):
        return "Not provided"

def render_project_content(project, index, total, previous, following):
    esc = lambda value: html.escape(str(value or ""), quote=True)
    topics = project.get("stack", [])[:6]
    chips = "".join(f"<li>{esc(topic)}</li>" for topic in topics)
    chips_markup = f'\n  <ul class="chips">{chips}</ul>' if chips else ""
    language = project.get("language") or "Not specified"
    return f"""<article class="project-page">
  <a class="page__crumb" href="../index.html#work">← All projects</a>
  <p class="page__pos">Project {index:02d} / {total:02d} · Git Guild repository</p>
  <h1 class="page__title">{esc(project['name'])}</h1>
  <p class="page__tagline">{esc(project.get('tagline'))}</p>
  <p class="page__blurb">{esc(project.get('blurb'))}</p>{chips_markup}
  <dl class="page__meta">
    <div><dt>Primary language</dt><dd>{esc(language)}</dd></div>
    <div><dt>Last updated</dt><dd>{esc(date_label(project.get('updatedAt')))}</dd></div>
  </dl>
  <div class="page__actions">
    <a class="btn btn--primary" href="{esc(project['url'])}" target="_blank" rel="noopener">Open repository <span aria-hidden="true">↗</span></a>
  </div>
  <nav class="page__stepnav" aria-label="Project navigation">
    <a class="page__step" href="../projects/{esc(previous['slug'])}.html">← {esc(previous['name'])}</a>
    <a class="page__step" href="../projects/{esc(following['slug'])}.html">{esc(following['name'])} →</a>
  </nav>
</article>"""

def write_project_pages(catalog, project_template, styles, mark_symbol, favicon_uri, theme_script):
    projects = catalog["projects"]
    order = catalog["order"]
    names = {}
    slug_counts = {}
    for project_id in order:
        project = projects[project_id]
        base = slugify(project["name"])
        slug = base
        suffix = 2
        while slug in slug_counts:
            slug = f"{base}-{suffix}"
            suffix += 1
        slug_counts[slug] = True
        project["slug"] = slug
        names[project_id] = project

    project_dir = os.path.join(ROOT, "gitguild", "projects")
    os.makedirs(project_dir, exist_ok=True)
    expected = {project["slug"] + ".html" for project in names.values()}
    manifest = os.path.join(project_dir, ".gitguild-generated-pages.json")
    previous = set()
    if os.path.exists(manifest):
        try:
            previous = set(json_file(manifest))
        except (ValueError, TypeError):
            previous = set()
    else:
        # This directory contains generated project pages in the documented pipeline.
        previous = {name for name in os.listdir(project_dir) if name.endswith(".html")}
    for stale in previous - expected:
        path = os.path.join(project_dir, stale)
        if os.path.isfile(path):
            os.unlink(path)

    total = len(order)
    for index, project_id in enumerate(order):
        project = names[project_id]
        prev = names[order[(index - 1) % total]]
        nxt = names[order[(index + 1) % total]]
        page = project_template.replace("__TITLE__", html.escape(project["name"], quote=True))
        page = page.replace("__DESCRIPTION__", html.escape(project["tagline"], quote=True))
        page = page.replace("__FAVICON__", favicon_uri).replace("__STYLES__", styles)
        page = page.replace("__THEME_SCRIPT__", theme_script)
        page = page.replace("__MARK_SYMBOL__", mark_symbol)
        page = page.replace("__HOME__", "../index.html")
        page = page.replace("__DOCS__", html.escape(catalog["collective"]["links"]["docs"], quote=True))
        page = page.replace("__GITHUB__", html.escape(catalog["collective"]["links"]["github"], quote=True))
        page = page.replace("__MAIL__", html.escape(catalog["collective"]["links"]["mail"], quote=True))
        page = page.replace("__GOODFIRST__", html.escape(catalog["collective"]["links"]["goodFirstIssues"], quote=True))
        page = page.replace("__LEGALBASE__", "../legal/")
        page = page.replace("__YEAR__", str(catalog["collective"]["since"]))
        page = page.replace("__COUNT__", str(total))
        page = page.replace("__CONTENT__", render_project_content(project, index + 1, total, prev, nxt))
        with open(os.path.join(project_dir, project["slug"] + ".html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(page)
    with open(manifest, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sorted(expected), f, indent=2)
        f.write("\n")

def main():
    template_path = os.path.join(SRC_DIR, "template.html")
    styles_path = os.path.join(SRC_DIR, "styles.css")
    geom_path = os.path.join(SRC_DIR, "emblem-geometry.js")
    curation_path = os.path.join(SRC_DIR, "project-curation.json")
    project_template_path = os.path.join(SRC_DIR, "project-template.html")
    app_path = os.path.join(SRC_DIR, "app.js")
    theme_path = os.path.join(SRC_DIR, "theme.js")
    favicon_path = os.path.join(ASSETS_DIR, "favicon.svg")
    vendor_dir = os.path.join(SRC_DIR, "vendor")
    react_path = os.path.join(vendor_dir, "react.production.min.js")
    react_dom_path = os.path.join(vendor_dir, "react-dom.production.min.js")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Missing template: {template_path}")

    template = read_file(template_path)
    styles = read_file(styles_path) if os.path.exists(styles_path) else ""
    geom = read_file(geom_path) if os.path.exists(geom_path) else ""
    if not os.path.exists(SNAPSHOT_PATH):
        raise FileNotFoundError(f"Missing project snapshot: {SNAPSHOT_PATH}; run tools/sync/sync_github_projects.py")
    snapshot = json_file(SNAPSHOT_PATH)
    curation = json_file(curation_path)
    catalog = build_catalog(snapshot, curation)
    projects = "window.GUILD = " + safe_script_json(catalog) + ";"
    project_template = read_file(project_template_path)
    app = read_file(app_path) if os.path.exists(app_path) else ""
    theme_script = read_file(theme_path) if os.path.exists(theme_path) else ""
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
  <symbol id="guild-mark" overflow="visible" viewBox="465.5 81.8 476.0 476.0">
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
    mark_symbol = mark_symbol.replace('stroke="#EBE8DB"', 'stroke="var(--bone)"')
    mark_symbol = mark_symbol.replace('stroke="#F4A330"', 'stroke="var(--amber)"')

    collective = catalog["collective"]
    links = collective["links"]
    lede = collective["lede"]
    github_link = links["github"]
    mail_link = links["mail"]
    docs_link = links["docs"]
    goodfirst_link = links["goodFirstIssues"]

    # Replace placeholders
    html = template
    html = html.replace("__FAVICON__", favicon_uri)
    html = html.replace("__STYLES__", styles)
    html = html.replace("__THEME_SCRIPT__", theme_script)
    html = html.replace("__MARK_SYMBOL__", mark_symbol)
    html = html.replace("__VIEW__", "465.5 81.8 476.0 476.0")
    html = html.replace("__LEDE__", lede)
    html = html.replace("__GITHUB__", github_link)
    html = html.replace("__DOCS__", docs_link)
    html = html.replace("__GOODFIRST__", goodfirst_link)
    html = html.replace("__MAIL__", mail_link)
    html = html.replace("__ACTIVE_NODE_COUNT__", str(min(len(catalog["order"]), 12)))
    html = html.replace("__PROJECTS__", projects)
    html = html.replace("__GEOMETRY__", geom)
    html = html.replace("__REACT__", react)
    html = html.replace("__REACT_DOM__", react_dom)
    html = html.replace("__APP__", app)

    with open(INDEX_HTML, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    write_project_pages(catalog, project_template, styles, mark_symbol, favicon_uri, theme_script)

    print(f"Successfully assembled {INDEX_HTML}")

if __name__ == "__main__":
    main()
