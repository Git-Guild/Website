"""Functional assertions against the built page."""
import asyncio, os, json
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
URL = "file://" + os.path.join(ROOT, "gitguild", "index.html")
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
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.on("console", lambda m: errs.append("console." + m.type + ": " + m.text) if m.type == "error" else None)
        await p.goto(URL)
        await p.wait_for_timeout(3300)

        # structure
        nodes = await p.locator(".node").count()
        cards = await p.locator(".card").count()
        commits = await p.locator(".commit").count()
        check("12 interactive nodes rendered", nodes == 12, nodes)
        check("12 project cards rendered", cards == 12, cards)
        check("6 merge-train commits rendered", commits == 6, commits)

        names = await p.eval_on_selector_all(".card__name", "els => els.map(e => e.textContent)")
        check("all cards have a name", all(n.strip() for n in names), names)
        node_ids = await p.eval_on_selector_all(".node", "els => els.map(e => e.dataset.id)")
        card_ids = await p.eval_on_selector_all(".card", "els => els.map(e => e.dataset.id)")
        check("card ids match node ids", sorted(node_ids) == sorted(card_ids), (node_ids, card_ids))
        check("every node has a trace wiring", await p.evaluate(
            "window.GUILD_GRID.adjacency && Object.values(window.GUILD_GRID.adjacency).every(v => v.length > 0)"))

        # hover a node lights its traces
        await p.locator('.node[data-id="n7"]').hover()
        await p.wait_for_timeout(400)
        lit = await p.eval_on_selector_all(".trace:not(.trace--halo).is-lit", "els => els.length")
        focused = await p.evaluate("document.getElementById('emblem').classList.contains('is-focused')")
        expect = await p.evaluate("window.GUILD_GRID.adjacency['n7'].length")
        exp_n7 = (await p.evaluate("window.GUILD.projects['n7'].name")).upper()
        check("hovering a node lights exactly its traces", lit == expect, f"{lit} vs {expect}")
        check("hover dims the rest of the emblem", focused)
        tip_on = await p.evaluate("document.getElementById('tip').classList.contains('is-on')")
        tip_txt = await p.locator("#tip .tip__name").inner_text()
        check("tooltip shows project name", tip_on and tip_txt.strip() == exp_n7, tip_txt)

        # train hover drives the emblem
        await p.evaluate("document.querySelector('.commit[data-id=\"n5\"]').dispatchEvent(new MouseEvent('mouseenter',{bubbles:false}))")
        await p.wait_for_timeout(300)
        hot = await p.evaluate("document.querySelector('.node[data-id=\"n5\"]').classList.contains('is-hot')")
        check("train commit hover highlights its emblem node", hot)

        # node click -> panel
        exp_n2 = (await p.evaluate("window.GUILD.projects['n2'].name")).upper()
        await p.locator('.node[data-id="n2"]').click()
        await p.wait_for_timeout(600)
        check("panel opens on node click", await p.evaluate("document.getElementById('panel').classList.contains('is-open')"))
        name = await p.locator('[data-bind="name"]').inner_text()
        check("panel shows the clicked project", name.strip() == exp_n2, name)
        url = await p.get_attribute('[data-bind="visit"]', "href")
        check("visit link present", url.startswith("http"), url)

        # panel nav + keyboard
        exp_next = (await p.evaluate("window.GUILD.projects[window.GUILD.order[(window.GUILD.order.indexOf('n2') + 1) % window.GUILD.order.length]].name")).upper()
        await p.locator('[data-bind="next"]').click(); await p.wait_for_timeout(500)
        n2_txt = await p.locator('[data-bind="name"]').inner_text()
        check("next advances the panel", n2_txt.strip() == exp_next, n2_txt)
        await p.keyboard.press("ArrowLeft"); await p.wait_for_timeout(500)
        n3_txt = await p.locator('[data-bind="name"]').inner_text()
        check("arrow-left steps back", n3_txt.strip() == exp_n2, n3_txt)
        await p.keyboard.press("Escape"); await p.wait_for_timeout(500)
        check("escape closes the panel", not await p.evaluate("document.getElementById('panel').classList.contains('is-open')"))

        # backdrop click closes
        await p.locator('.node[data-id="n4"]').click(); await p.wait_for_timeout(500)
        await p.mouse.click(200, 500)
        await p.wait_for_timeout(500)
        check("clicking the backdrop closes the panel", not await p.evaluate("document.getElementById('panel').classList.contains('is-open')"))

        # keyboard traversal on the emblem
        exp_n3 = (await p.evaluate("window.GUILD.projects['n3'].name")).upper()
        await p.locator('.node[data-id="n0"]').focus()
        await p.keyboard.press("ArrowRight")
        focused_id = await p.evaluate("document.activeElement.dataset ? document.activeElement.dataset.id : null")
        check("arrow keys move focus between nodes", focused_id == "n3", focused_id)
        await p.keyboard.press("Enter"); await p.wait_for_timeout(500)
        check("enter opens the focused project", (await p.locator('[data-bind="name"]').inner_text()).strip() == exp_n3)
        await p.keyboard.press("Escape")

        # copy button
        await p.evaluate("document.getElementById('join').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(400)
        await p.locator("[data-copy]").click(); await p.wait_for_timeout(300)
        lbl = await p.locator(".copy__label").inner_text()
        check("copy button gives feedback", lbl.strip().lower() == "copied", lbl)

        # a11y basics
        no_name = await p.evaluate("""(() => {
          const bad = [];
          document.querySelectorAll('.node').forEach(n => { if(!n.getAttribute('aria-label')) bad.push(n.dataset.id); });
          document.querySelectorAll('.card').forEach(c => { if(!c.getAttribute('aria-label')) bad.push(c.dataset.id); });
          return bad;
        })()""")
        check("all interactive elements are labelled", len(no_name) == 0, no_name)
        check("no console/page errors", len(errs) == 0, errs[:4])

        await b.close()


asyncio.run(main())
print("\n" + ("ALL CHECKS PASSED" if not FAIL else f"{len(FAIL)} FAILURES: {FAIL}"))
