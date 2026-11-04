"""Functional assertions over the offline homepage and generated repository pages."""
import asyncio
import json
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOME_PATH = os.path.join(ROOT, "gitguild", "index.html")
HOME = "file://" + HOME_PATH
FAIL = []


def check(label, condition, detail=""):
    print(("PASS  " if condition else "FAIL  ") + label + ((" :: " + str(detail)) if detail else ""))
    if not condition:
        FAIL.append(label)


async def main():
    with open(os.path.join(ROOT, "data", "github-projects.json"), encoding="utf-8") as f:
        snapshot = json.load(f)
    repos = {item["name"]: item for item in snapshot["repositories"]}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 940})
        errors, external = [], []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: errors.append("console." + msg.type + ": " + msg.text) if msg.type == "error" else None)
        page.on("request", lambda req: external.append(req.url) if req.url.startswith("http") else None)
        await page.goto(HOME)
        await page.wait_for_timeout(1500)

        data = await page.evaluate("""() => ({
          order: window.GUILD.order,
          projects: window.GUILD.projects,
          slots: [...document.querySelectorAll('.node')].map(n => ({id:n.dataset.id, inactive:n.classList.contains('node--inactive')})),
          slides: [...document.querySelectorAll('.slide')].map(n => n.dataset.id),
          rows: [...document.querySelectorAll('.sidx__row')].map(n => n.dataset.id),
          dots: [...document.querySelectorAll('.dot')].map(n => n.dataset.id),
          updates: [...document.querySelectorAll('.commit')].map(n => n.dataset.id),
          overflow: [...document.querySelectorAll('.overflow__row')].map(n => n.getAttribute('href'))
        })""")
        ids = data["order"]
        active_ids = ids[:12]
        check("React runtime is inlined", await page.evaluate("!!window.React && !!window.ReactDOM"))
        check("emblem is mounted through React", await page.evaluate("!!window.GuildEmblem && !!window.GuildEmblem.pageUrl"))
        check("home loads without network requests", not external, external[:3])
        check("12 physical rings remain; active rings match repository count",
              len(data["slots"]) == 12 and sum(not x["inactive"] for x in data["slots"]) == min(len(ids), 12), data["slots"])
        check("slider, index and dots bind only to ordered repositories",
              all(data[key] == active_ids for key in ("slides", "rows", "dots")),
              {key: data[key] for key in ("slides", "rows", "dots")})
        starter_labels = await page.eval_on_selector_all(".sidx__path", "els => els.map(el => el.textContent.trim())")
        check("beginner curriculum repositories are marked as learning tracks",
              starter_labels == ["Learning track"] * 3 and
              all(data["projects"][key].get("pathLabel") == "Learning track" for key in active_ids[:3]), starter_labels)
        inactive_link_tabs = await page.eval_on_selector_all(
            ".slide[aria-hidden='true'] .slide__actions a", "els => els.map(el => el.tabIndex)")
        check("hidden carousel slides keep their detail links out of the tab order",
              all(value == -1 for value in inactive_link_tabs), inactive_link_tabs)
        check("overflow projects stay reachable from the browser",
              len(data["overflow"]) == max(0, len(ids) - 12), data["overflow"])
        check("recent-update timeline is built from snapshot records", len(data["updates"]) == min(6, len(ids)) and set(data["updates"]).issubset(ids), data["updates"])
        for repo_name, repo in repos.items():
            check("project link maps to GitHub: " + repo_name,
                  any(p.get("repoName") == repo_name and p.get("url") == repo["html_url"] for p in data["projects"].values()))
        check("placeholder chat and fictional merge claims are absent",
              "discord.com" not in (await page.locator("body").inner_text()).lower() and
              "merge train" not in (await page.locator("body").inner_text()).lower())

        first = active_ids[min(1, len(active_ids) - 1)]
        project = data["projects"][first]
        slug = await page.evaluate("id => window.GuildEmblem.pageUrl(id)", first)
        node = page.locator(f'.node[data-id="{first}"]')
        await node.hover()
        await page.wait_for_timeout(200)
        adjacency = await page.evaluate("id => window.GUILD_GRID.adjacency[id].length", first)
        lit = await page.locator(".trace:not(.trace--halo).is-lit").count()
        check("hover lights exactly the selected ring wiring", lit == adjacency, (lit, adjacency))
        check("tooltip exposes repository name and summary",
              await page.locator("#tip").get_attribute("aria-hidden") == "false" and
              (await page.locator("#tip .tip__name").inner_text()).strip() == project["name"].upper())

        await node.click()
        await page.wait_for_timeout(700)
        selection_state = await page.evaluate("""id => ({
          url: location.href,
          selected: document.querySelector('.node[data-id="' + id + '"]')?.classList.contains('is-selected'),
          spotlight: document.querySelector('.spot__name')?.textContent,
          expected: window.GUILD.projects[id]?.name
        })""", first)
        check("ring selection stays on the homepage and updates spotlight",
              "projects/" not in selection_state["url"] and selection_state["selected"] and
              selection_state["spotlight"] == selection_state["expected"], selection_state)
        repo_action = page.locator(".spot__repo")
        check("selected project has a direct GitHub repository action",
              await repo_action.get_attribute("href") == project["url"] and
              await repo_action.get_attribute("target") == "_blank")
        await page.locator(".spot__details").click()
        await page.wait_for_timeout(500)
        check("spotlight opens the generated repository page", page.url.endswith("/" + slug), page.url)
        check("repository page shows curated title and summary",
              (await page.locator(".page__title").inner_text()).strip() == project["name"].upper() and
              bool((await page.locator(".page__blurb").inner_text()).strip()))
        target = await page.get_attribute(".page__actions a.btn--primary", "href")
        check("repository page points directly to the real GitHub repository", target == project["url"], target)
        dates = await page.locator(".page__meta").inner_text()
        expected_date = datetime.fromisoformat(project["updatedAt"].replace("Z", "+00:00")).strftime("%d %b %Y")
        check("repository page shows its factual update date", expected_date in dates, dates)
        await page.locator(".page__crumb").click()
        await page.wait_for_timeout(500)
        check("repository page links back to the browser", "#work" in page.url, page.url)

        nav = await page.eval_on_selector_all("#navlinks a", "els => els.map(e => e.textContent.trim())")
        check("section navigation uses current homepage labels", nav == ["Projects", "Recent updates", "Manifesto", "Docs", "Join"], nav)
        check("join actions offer issues and organization links",
              await page.locator('.join__actions a[href*="issues?q="]').count() == 1 and
              await page.locator('.join__actions a[href="https://github.com/Git-Guild"]').count() == 1)

        await page.set_viewport_size({"width": 390, "height": 844})
        await page.locator("[data-menu]").click()
        check("mobile menu toggles accessible expanded state",
              await page.get_attribute("[data-menu]", "aria-expanded") == "true")
        await page.locator("[data-menu]").click()
        await page.evaluate("window.scrollTo(0,0)")
        for width, height in ((390, 844), (360, 640)):
            await page.set_viewport_size({"width": width, "height": height})
            cta = await page.locator(".hero__cta--mobile a").first.bounding_box()
            check(f"primary mobile action visible at {width}x{height}", bool(cta and cta["y"] < height), cta)
        await page.set_viewport_size({"width": 1440, "height": 940})
        await page.locator(f'.node[data-id="{first}"]').focus()
        await page.keyboard.press("Enter")
        check("keyboard Enter selects a focused active ring",
              await page.locator(f'.node[data-id="{first}"]').evaluate("el => el.classList.contains('is-selected')"))
        await page.keyboard.press("ArrowRight")
        next_id = active_ids[(active_ids.index(first) + 1) % len(active_ids)]
        check("arrow key moves focus between active rings",
              await page.evaluate("document.activeElement.dataset.id") == next_id, next_id)
        await page.keyboard.press("Enter")
        await page.keyboard.press("Escape")
        check("Escape clears the ring selection", await page.locator(".node.is-selected").count() == 0)

        await page.evaluate("""async () => {
          const step = Math.max(320, Math.floor(innerHeight * 0.8));
          for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
            scrollTo(0, y);
            await new Promise(resolve => setTimeout(resolve, 60));
          }
          scrollTo(0, 0);
        }""")
        reveal_state = await page.evaluate("""() => ({
          total: document.querySelectorAll('.reveal').length,
          visible: document.querySelectorAll('.reveal.in').length
        })""")
        check("scroll reveals every content section", reveal_state["visible"] == reveal_state["total"], reveal_state)

        reduced = await browser.new_context(viewport={"width": 1440, "height": 940}, reduced_motion="reduce")
        reduced_page = await reduced.new_page()
        await reduced_page.goto(HOME)
        await reduced_page.wait_for_timeout(250)
        motion_duration = await reduced_page.locator(".eyebrow__dot").evaluate("el => getComputedStyle(el).animationDuration")
        check("reduced-motion mode renders rings with near-zero animation",
              await reduced_page.locator(".node").count() == 12 and motion_duration in ("1e-06s", "0.000001s"), motion_duration)
        await reduced.close()
        check("no browser errors", not errors, errors[:5])
        await browser.close()


asyncio.run(main())
print("\n" + ("ALL CHECKS PASSED" if not FAIL else f"{len(FAIL)} FAILURES: {FAIL}"))
if FAIL:
    raise SystemExit(1)
