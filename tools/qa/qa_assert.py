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
        slides = await p.locator(".slide").count()
        index_rows = await p.locator(".sidx__row").count()
        dots = await p.locator(".dot").count()
        commits = await p.locator(".commit").count()
        check("12 emblem slots rendered", nodes == 12, nodes)
        check("slider holds all 12 slotted projects", slides == 12 and index_rows == 12 and dots == 12,
              (slides, index_rows, dots))
        check("6 merge-train commits rendered", commits == 6, commits)
        node_ids = await p.eval_on_selector_all(".node", "els => els.map(e => e.dataset.id)")
        order = await p.evaluate("window.GUILD.order")
        check("emblem follows order[:12] slots", node_ids == order[:12], (node_ids, order[:12]))
        card_ids = await p.eval_on_selector_all(".slide", "els => els.map(e => e.dataset.id)")
        check("slides follow order[:12] in order", card_ids == order[:12], (card_ids, order[:12]))
        check("every node has a trace wiring", await p.evaluate(
            "window.GUILD_GRID.adjacency && Object.values(window.GUILD_GRID.adjacency).every(v => v.length > 0)"))
        names = await p.eval_on_selector_all(".slide__name", "els => els.map(e => e.textContent)")
        check("all slides have a name", all(n.strip() for n in names))
        slide_a11y = await p.evaluate("""(() => {
          const slides = [...document.querySelectorAll('.slide')];
          const badLabel = slides.filter(s => !/^\\d+ of \\d+: .+/.test(s.getAttribute('aria-label') || ''));
          const tabbable = slides.filter(s => s.getAttribute('tabindex') === '0');
          const hidden = slides.filter(s => s.getAttribute('tabindex') === '-1' && s.getAttribute('aria-hidden') === 'true' && s.inert === true);
          return { total: slides.length, badLabel: badLabel.length, tabbable: tabbable.length, hidden: hidden.length };
        })()""")
        check("only the active slide is focusable and labelled",
              slide_a11y["total"] == 12 and slide_a11y["badLabel"] == 0 and
              slide_a11y["tabbable"] == 1 and slide_a11y["hidden"] == 11, slide_a11y)

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

        # index + train cross-highlight
        await p.locator('.sidx__row[data-id="n0"]').hover()
        await p.wait_for_timeout(300)
        check("index hover highlights its node",
              await p.evaluate("document.querySelector('.node[data-id=\"n0\"]').classList.contains('is-hot')"))
        await p.evaluate("document.getElementById('merge-train').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(400)
        await p.locator('.commit[data-id="n5"]').hover()
        await p.wait_for_timeout(300)
        check("train commit hover highlights its node",
              await p.evaluate("document.querySelector('.node[data-id=\"n5\"]').classList.contains('is-hot')"))

        # ADR-0003 step 2: ring tap selects only (no navigation); chip jumps to work
        await p.evaluate("window.scrollTo(0,0)")
        await p.wait_for_timeout(400)
        await p.locator('.node[data-id="n8"]').click()
        await p.wait_for_timeout(800)
        check("ring tap selects without navigating",
              "projects/" not in p.url and
              await p.evaluate("document.querySelector('.node[data-id=\"n8\"]').classList.contains('is-selected')"),
              p.url)
        chip_txt = await p.locator(".sel-chip").inner_text()
        check("off-screen selection raises the View chip",
              await p.locator(".sel-chip:not([hidden])").count() == 1 and
              "03/12 VECTOR" in chip_txt.upper() and "VIEW" in chip_txt.upper(), chip_txt)
        await p.locator(".sel-chip").click()
        await p.wait_for_timeout(1400)
        check("chip scrolls to the work section",
              await p.evaluate("(() => { const r = document.getElementById('work').getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; })()"))
        check("selection persists after chip jump",
              await p.evaluate("document.querySelector('.node[data-id=\"n8\"]').classList.contains('is-selected')"))

        # prev/next step through the same state machine and keep focus
        await p.locator(".slider__step[aria-label='Next project']").click()
        await p.wait_for_timeout(600)
        count = await p.locator(".slider__count").inner_text()
        check("next advances the counter, spotlight, and emblem",
              "04 / 12" in count and
              "FERRY" in (await p.locator(".spot__name").inner_text()).upper() and
              await p.evaluate("document.querySelector('.node[data-id=\"n10\"]').classList.contains('is-selected')") and
              await p.evaluate("document.activeElement.getAttribute('aria-label')") == "Next project", count)
        await p.locator(".slider__step[aria-label='Previous project']").click()
        await p.wait_for_timeout(600)
        check("prev returns to the selected project",
              "03 / 12" in (await p.locator(".slider__count").inner_text()) and
              "VECTOR" in (await p.locator(".spot__name").inner_text()).upper())

        # the spotlight Open action navigates to the project page
        check("spotlight announces selection politely",
              await p.get_attribute("#spotlight", "aria-live") == "polite")
        await p.locator(".spot__open").click()
        await p.wait_for_timeout(1500)
        check("spotlight Open navigates to the project page", "projects/vector.html" in p.url, p.url)
        check("project page shows name", (await p.locator(".page__title").inner_text()).strip() == "VECTOR")
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

        # mobile carousel: dots jump, counter follows
        await p.set_viewport_size({"width": 390, "height": 844})
        await p.wait_for_timeout(500)
        await p.locator('.dot[data-id="n2"]').click()
        await p.wait_for_timeout(800)
        check("dots jump to the project on mobile",
              "08 / 12" in (await p.locator(".slider__count").inner_text()) and
              await p.evaluate("document.querySelector('.node[data-id=\"n2\"]').classList.contains('is-selected')"))
        # swipe settles onto the swiped slide (synthetic gesture + track scroll)
        await p.evaluate("""(() => {
          const track = document.querySelector('.carousel__track');
          track.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
          track.scrollLeft = track.querySelectorAll('.slide')[3].offsetLeft;
        })()""")
        await p.wait_for_timeout(700)
        check("swipe settles onto the swiped slide",
              "04 / 12" in (await p.locator(".slider__count").inner_text()) and
              await p.evaluate("document.querySelector('.node[data-id=\"n10\"]').classList.contains('is-selected')"))
        # ADR-0003 step 4: mobile CTA hierarchy + hero compaction
        await p.evaluate("window.scrollTo(0,0)")
        await p.wait_for_timeout(400)
        mobile_ctas = await p.evaluate("[...document.querySelectorAll('.hero__cta--mobile a')].filter(a => a.offsetParent !== null).map(a => a.getAttribute('href'))")
        check("mobile primary CTA joins the chat",
              len(mobile_ctas) == 2 and mobile_ctas[0].rstrip('/') == "https://discord.com" and mobile_ctas[1] == "#work",
              mobile_ctas)
        hero390 = await p.evaluate("""(() => {
          const stage = document.querySelector('.stage');
          const ctas = [...document.querySelectorAll('.hero__cta--mobile a')].map(a => ({
            top: Math.round(a.getBoundingClientRect().top),
            seen: getComputedStyle(a).opacity === '1'
          }));
          const lede = (document.querySelector('.lede') || {}).textContent || '';
          const wordmark = parseFloat(getComputedStyle(document.querySelector('.wordmark')).fontSize);
          return { stage: Math.round(stage.getBoundingClientRect().width), ctas, lede: lede.length, wordmark: Math.round(wordmark) };
        })()""")
        check("emblem capped for small screens", hero390["stage"] <= 280, hero390["stage"])
        check("lede slot stays 90-120 chars", 90 <= hero390["lede"] <= 120, hero390["lede"])
        check("wordmark compacts to 30px", hero390["wordmark"] == 30, hero390["wordmark"])
        check("primary CTA clears 390x844",
              all(c["top"] < 844 and c["seen"] for c in hero390["ctas"]), hero390["ctas"])
        await p.set_viewport_size({"width": 360, "height": 640})
        await p.wait_for_timeout(500)
        await p.evaluate("window.scrollTo(0,0)")
        await p.wait_for_timeout(400)
        ctas360 = await p.evaluate("[...document.querySelectorAll('.hero__cta--mobile a')].map(a => ({ top: Math.round(a.getBoundingClientRect().top), seen: getComputedStyle(a).opacity === '1' }))")
        check("primary CTA clears 360x640",
              all(c["top"] < 640 and c["seen"] for c in ctas360), ctas360)
        await p.set_viewport_size({"width": 1440, "height": 940})
        await p.wait_for_timeout(400)
        # ADR-0003 step 4: desktop CTA hierarchy (Browse primary, chat secondary)
        desktop_ctas = await p.evaluate("[...document.querySelectorAll('.hero__cta--desktop a')].filter(a => a.offsetParent !== null).map(a => a.getAttribute('href'))")
        check("desktop primary CTA browses projects",
              desktop_ctas == ["#work", "https://discord.com/"], desktop_ctas)

        # keyboard traversal + select-only + escape clears selection
        await p.locator('.node[data-id="n0"]').focus()
        await p.keyboard.press("ArrowRight")
        fid = await p.evaluate("document.activeElement.dataset ? document.activeElement.dataset.id : null")
        check("arrow keys move focus between nodes", fid == "n3", fid)
        await p.keyboard.press("Enter")
        await p.wait_for_timeout(400)
        check("enter selects the focused ring without navigating",
              "projects/" not in p.url and
              await p.evaluate("document.querySelector('.node[data-id=\"n3\"]').classList.contains('is-selected')"),
              p.url)
        await p.keyboard.press("Escape")
        await p.wait_for_timeout(400)
        check("escape clears the selection",
              await p.evaluate("document.querySelectorAll('.node.is-selected').length") == 0)

        # copy button
        await p.evaluate("document.getElementById('join').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(400)
        await p.locator("[data-copy]").click()
        await p.wait_for_timeout(300)
        check("copy button gives feedback",
              (await p.locator(".copy__label").inner_text()).strip().lower() == "copied")

        # ADR-0003 step 1: placeholder-link guard (fails until real links land)
        chat_href = await p.get_attribute('.join__actions a.btn--ghost', 'href')
        check("chat CTA is a real invite, not the bare placeholder",
              chat_href and chat_href.rstrip('/') not in ('https://discord.com', 'https://discord.gg'), chat_href)
        bare = await p.evaluate("""(() => {
          const bare = [];
          for (const [id, pr] of Object.entries(window.GUILD.projects || {})) {
            for (const f of ['url', 'repo', 'docs']) {
              if (pr[f] && pr[f].replace(/\\/$/, '') === 'https://github.com') bare.push(id + '.' + f);
            }
          }
          return bare;
        })()""")
        check("no bare project URL placeholders", len(bare) == 0, bare[:6])

        # a11y + reduced motion + cleanliness
        bad = await p.evaluate("""(() => {
          const bad = [];
          document.querySelectorAll('.node').forEach(n => { if(!n.getAttribute('aria-label')) bad.push(n.dataset.id); });
          document.querySelectorAll('.slide').forEach(s => { if(!s.getAttribute('aria-label')) bad.push('slide:'+s.dataset.id); });
          document.querySelectorAll('.sidx__row').forEach(r => { if(!r.getAttribute('aria-label')) bad.push('index:'+r.dataset.id); });
          document.querySelectorAll('.dot').forEach(d => { if(!d.getAttribute('aria-label')) bad.push('dot:'+d.dataset.id); });
          document.querySelectorAll('.commit').forEach(c => { if(!c.getAttribute('aria-label')) bad.push('commit:'+c.dataset.id); });
          return bad;
        })()""")
        check("every node, slide, index row, dot, and commit is labelled", len(bad) == 0, bad)
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
