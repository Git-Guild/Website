"""Extended functional assertions over the built output (home + project + legal pages)."""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOME = "file://" + os.path.join(ROOT, "gitguild", "index.html")
PROJ = lambda slug: "file://" + os.path.join(ROOT, "gitguild", "projects", slug + ".html")
FAIL = []


def check(label, cond, extra=""):
    print(("PASS  " if cond else "FAIL  ") + label + ((" :: " + str(extra)) if extra else ""))
    if not cond:
        FAIL.append(label)


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        p = await b.new_page(viewport={"width": 1440, "height": 940})
        errs = []
        ext = []
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.on("console", lambda m: errs.append("console." + m.type + ": " + m.text) if m.type == "error" else None)
        p.on("request", lambda r: ext.append(r.url) if r.url.startswith("http") else None)
        await p.goto(HOME)
        await p.wait_for_timeout(3500)

        # foundation: React UMD inlined, offline shell
        check("React UMD runtime inlined", await p.evaluate("!!window.React && !!window.ReactDOM"))
        check("emblem renders through React shell", await p.evaluate("!!window.GuildEmblem && !!window.GuildEmblem.pageUrl"))
        check("no external requests on home", len(ext) == 0, ext[:3])

        # structure + slots
        nodes = await p.locator(".node").count()
        cards = await p.locator(".card").count()
        commits = await p.locator(".commit").count()
        check("12 emblem slots rendered", nodes == 12, nodes)
        check("12 project cards rendered", cards == 12, cards)
        check("6 merge-train commits rendered", commits == 6, commits)
        node_ids = await p.eval_on_selector_all(".node", "els => els.map(e => e.dataset.id)")
        order = await p.evaluate("window.GUILD.order")
        check("emblem follows order[:12] slots", node_ids == order[:12], (node_ids, order[:12]))
        card_ids = await p.eval_on_selector_all(".card", "els => els.map(e => e.dataset.id)")
        check("work section lists all projects in order", card_ids == order, (card_ids, order))
        check("every node has a trace wiring", await p.evaluate(
            "window.GUILD_GRID.adjacency && Object.values(window.GUILD_GRID.adjacency).every(v => v.length > 0)"))
        names = await p.eval_on_selector_all(".card__name", "els => els.map(e => e.textContent)")
        check("all cards have a name", all(n.strip() for n in names))

        # hover wiring exactness + tooltip content
        await p.locator('.node[data-id="n7"]').hover()
        await p.wait_for_timeout(400)
        lit = await p.eval_on_selector_all(".trace:not(.trace--halo).is-lit", "els => els.length")
        expect = await p.evaluate("window.GUILD_GRID.adjacency['n7'].length")
        check("hovering a node lights exactly its wiring", lit == expect, f"{lit} vs {expect}")
        check("hover dims the rest of the emblem",
              await p.evaluate("document.getElementById('emblem').classList.contains('is-focused')"))
        tip_on = await p.evaluate("document.getElementById('tip').classList.contains('is-on')")
        tip_name = await p.locator("#tip .tip__name").inner_text()
        tip_tag = await p.locator("#tip .tip__tag").inner_text()
        check("tooltip shows name and tagline", tip_on and tip_name.strip() == "LOOM" and len(tip_tag.strip()) > 0,
              (tip_name, tip_tag))

        # card + train cross-highlight
        await p.locator('.card[data-id="n0"]').hover()
        await p.wait_for_timeout(300)
        check("card hover highlights its node",
              await p.evaluate("document.querySelector('.node[data-id=\"n0\"]').classList.contains('is-hot')"))
        await p.evaluate("document.getElementById('merge-train').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(400)
        await p.locator('.commit[data-id="n5"]').hover()
        await p.wait_for_timeout(300)
        check("train commit hover highlights its node",
              await p.evaluate("document.querySelector('.node[data-id=\"n5\"]').classList.contains('is-hot')"))

        # node click navigates to the project page
        await p.evaluate("window.scrollTo(0,0)")
        await p.wait_for_timeout(400)
        await p.locator('.node[data-id="n2"]').click()
        await p.wait_for_timeout(1500)
        check("node click navigates to the project page", "projects/lattice.html" in p.url, p.url)
        check("project page shows name", (await p.locator(".page__title").inner_text()).strip() == "LATTICE")
        check("project page shows tagline", len((await p.locator(".page__tagline").inner_text()).strip()) > 0)
        check("project page shows blurb", len((await p.locator(".page__blurb").inner_text()).strip()) > 0)
        check("project page shows stack chips", await p.locator(".page .chips li").count() >= 3)
        visit = await p.get_attribute(".page__actions a.btn--primary", "href")
        check("project page has Visit action", visit and visit.startswith("http"), visit)
        back = await p.get_attribute(".page__crumb", "href")
        check("project page links back to work", back and "index.html#work" in back, back)
        steps = await p.eval_on_selector_all(".page__step", "els => els.map(e => e.getAttribute('href'))")
        check("project page has prev/next", len(steps) == 2 and all(s.endswith(".html") for s in steps), steps)

        # missing optional links hide their buttons (anchor has docs: null)
        await p.goto(PROJ("anchor"))
        await p.wait_for_timeout(800)
        actions_txt = await p.locator(".page__actions").inner_text()
        check("missing Docs hides its button without breakage", "Docs" not in actions_txt, actions_txt[:120])

        # prev/next follows ordering; back-to-work returns home
        await p.goto(PROJ("anchor"))
        await p.wait_for_timeout(600)
        nxt = await p.eval_on_selector_all(".page__step", "els => els.map(e => e.getAttribute('href'))")
        check("prev/next steps through ordering", nxt == ["prism.html", "beacon.html"], nxt)
        await p.locator(".page__crumb").click()
        await p.wait_for_timeout(1200)
        check("back-to-work returns to the work section", "#work" in p.url, p.url)

        # nav resolves from project pages
        await p.goto(PROJ("beacon"))
        await p.wait_for_timeout(600)
        await p.locator('#navlinks a[href$="#merge-train"]').click()
        await p.wait_for_timeout(1200)
        check("nav resolves to home sections from project pages", "index.html#merge-train" in p.url, p.url)

        # footer + legal
        await p.goto(HOME)
        await p.wait_for_timeout(3000)
        check("footer has four groups", await p.locator(".footer__group").count() == 4)
        check("footer has good-first-issues entry",
              await p.locator('.footer__group[aria-label="Collective"] a:has-text("Good-first")').count() == 1)
        check("bottom bar has copyright, license, back-to-top",
              await p.locator('.footer__bar a[href="#top"]').count() == 1 and
              "MIT" in await p.locator(".footer__bar").inner_text())
        for legal in ("privacy", "terms", "license", "security"):
            await p.goto("file://" + os.path.join(ROOT, "gitguild", "legal", legal + ".html"))
            await p.wait_for_timeout(500)
            body = await p.locator(".page__body, .page__blurb").first.inner_text()
            check(f"legal page {legal} states no tracking / open terms",
                  ("no " in body.lower() or "MIT" in body or "track" in body.lower()), body[:80])

        # nav contract on home
        await p.goto(HOME)
        await p.wait_for_timeout(3000)
        nav_txt = await p.eval_on_selector_all("#navlinks a", "els => els.map(e => e.textContent.trim())")
        check("nav offers Projects, Merge train, Manifesto, Docs, Join",
              nav_txt == ["Projects", "Merge train", "Manifesto", "Docs", "Join"], nav_txt)
        await p.set_viewport_size({"width": 390, "height": 844})
        await p.wait_for_timeout(500)
        await p.locator("[data-menu]").click()
        await p.wait_for_timeout(300)
        check("mobile menu opens with expanded state",
              await p.evaluate("document.body.classList.contains('menu-open')") and
              await p.get_attribute("[data-menu]", "aria-expanded") == "true")
        await p.locator("[data-menu]").click()
        await p.wait_for_timeout(300)
        await p.set_viewport_size({"width": 1440, "height": 940})
        await p.wait_for_timeout(400)

        # keyboard traversal + quick-view panel + escape
        await p.locator('.node[data-id="n0"]').focus()
        await p.keyboard.press("ArrowRight")
        fid = await p.evaluate("document.activeElement.dataset ? document.activeElement.dataset.id : null")
        check("arrow keys move focus between nodes", fid == "n3", fid)
        await p.evaluate("document.querySelector('[data-quick=\"n2\"]').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(300)
        await p.locator('[data-quick="n2"]').click()
        await p.wait_for_timeout(500)
        check("quick view opens the panel", await p.evaluate("document.getElementById('panel').classList.contains('is-open')"))
        check("panel shows name and project-page link",
              (await p.locator('[data-bind="name"]').inner_text()).strip() == "LATTICE" and
              (await p.get_attribute('[data-bind="page"]', "href") or "").endswith(".html"))
        await p.locator('[data-bind="next"]').click()
        await p.wait_for_timeout(400)
        check("panel next advances", (await p.locator('[data-bind="name"]').inner_text()).strip() == "GUILD CLI")
        await p.keyboard.press("Escape")
        await p.wait_for_timeout(400)
        check("escape closes the panel",
              not await p.evaluate("document.getElementById('panel').classList.contains('is-open')"))

        # copy button
        await p.evaluate("document.getElementById('join').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(400)
        await p.locator("[data-copy]").click()
        await p.wait_for_timeout(300)
        check("copy button gives feedback",
              (await p.locator(".copy__label").inner_text()).strip().lower() == "copied")

        # a11y + reduced motion + cleanliness
        bad = await p.evaluate("""(() => {
          const bad = [];
          document.querySelectorAll('.node').forEach(n => { if(!n.getAttribute('aria-label')) bad.push(n.dataset.id); });
          document.querySelectorAll('.card').forEach(c => { if(!c.getAttribute('aria-label')) bad.push('card:'+c.dataset.id); });
          document.querySelectorAll('.commit').forEach(c => { if(!c.getAttribute('aria-label')) bad.push('commit:'+c.dataset.id); });
          return bad;
        })()""")
        check("every node, card, and commit is labelled", len(bad) == 0, bad)
        ctx2 = await b.new_context(viewport={"width": 1440, "height": 940}, reduced_motion="reduce")
        pr = await ctx2.new_page()
        rerrs = []
        pr.on("pageerror", lambda e: rerrs.append(str(e)))
        await pr.goto(HOME)
        await pr.wait_for_timeout(3000)
        check("reduced-motion page renders with no errors",
              await pr.locator(".node").count() == 12 and len(rerrs) == 0, rerrs[:3])
        await ctx2.close()
        check("no console or page errors anywhere", len(errs) == 0, errs[:4])

        await b.close()


asyncio.run(main())
print("\n" + ("ALL CHECKS PASSED" if not FAIL else f"{len(FAIL)} FAILURES: {FAIL}"))
