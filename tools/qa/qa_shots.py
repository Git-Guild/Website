"""Screenshot + interaction QA for gitguild/index.html."""
import asyncio, os, sys
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
URL = "file://" + os.path.join(ROOT, "gitguild", "index.html")
OUT = os.path.join(ROOT, "build", "qa")
os.makedirs(OUT, exist_ok=True)
issues = []


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        p = await b.new_page(viewport={"width": 1440, "height": 940})
        p.on("console", lambda m: issues.append(f"console.{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        p.on("pageerror", lambda e: issues.append(f"pageerror: {e}"))
        await p.goto(URL)
        await p.wait_for_timeout(3400)
        await p.screenshot(path=f"{OUT}/01-hero.png")

        n = p.locator('.node[data-id="n3"]')
        await n.hover(); await p.wait_for_timeout(650)
        await p.screenshot(path=f"{OUT}/02-hover-node.png")

        await n.click(); await p.wait_for_timeout(800)
        await p.screenshot(path=f"{OUT}/03-panel.png")

        # panel next/prev then verify content swapped
        await p.locator('[data-bind="next"]').click()
        await p.wait_for_timeout(700)
        name = await p.locator('[data-bind="name"]').inner_text()
        issues.append(f"panel after next -> {name}")
        await p.screenshot(path=f"{OUT}/03b-panel-next.png")
        await p.keyboard.press("Escape"); await p.wait_for_timeout(500)

        # keyboard: tab into the emblem and open a node with Enter
        await p.locator('.node[data-id="n0"]').focus()
        await p.keyboard.press("Enter")
        await p.wait_for_timeout(700)
        kname = await p.locator('[data-bind="name"]').inner_text()
        issues.append(f"keyboard open -> {kname}")
        await p.keyboard.press("Escape"); await p.wait_for_timeout(400)

        # anchor scroll offset check
        await p.evaluate("location.hash = '#work'")
        await p.wait_for_timeout(900)
        await p.screenshot(path=f"{OUT}/04-cards.png")

        card = p.locator(".card").nth(4)
        await card.hover(); await p.wait_for_timeout(500)
        await p.screenshot(path=f"{OUT}/05-card-hover.png")

        # merge train
        await p.evaluate("document.getElementById('train-title').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(800)
        await p.locator(".commit").nth(3).hover()
        await p.wait_for_timeout(500)
        await p.screenshot(path=f"{OUT}/06-train.png")

        await p.evaluate("document.getElementById('join').scrollIntoView({block:'center'})"); await p.wait_for_timeout(800)
        await p.screenshot(path=f"{OUT}/07-join.png")

        await p.evaluate("document.getElementById('manifesto').scrollIntoView({block:'start'})"); await p.wait_for_timeout(700)
        await p.screenshot(path=f"{OUT}/07b-manifesto.png")

        await p.evaluate("window.scrollTo(0,0)"); await p.wait_for_timeout(400)
        await p.screenshot(path=f"{OUT}/08-full.png", full_page=True)

        # mobile
        m = await b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        m.on("pageerror", lambda e: issues.append(f"[mobile] pageerror: {e}"))
        await m.goto(URL); await m.wait_for_timeout(3200)
        await m.screenshot(path=f"{OUT}/09-mobile-hero.png")
        await m.locator('.node[data-id="n9"]').tap(); await m.wait_for_timeout(900)
        await m.screenshot(path=f"{OUT}/10-mobile-panel.png")
        await m.locator('.panel__close').tap(); await m.wait_for_timeout(500)
        await m.locator("#work").scroll_into_view_if_needed(); await m.wait_for_timeout(700)
        await m.screenshot(path=f"{OUT}/11-mobile-cards.png")
        await m.evaluate("document.getElementById('train-title').scrollIntoView({block:'start'})"); await m.wait_for_timeout(700)
        await m.screenshot(path=f"{OUT}/12-mobile-train.png")

        # tablet
        t = await b.new_page(viewport={"width": 820, "height": 1100})
        await t.goto(URL); await t.wait_for_timeout(3000)
        await t.screenshot(path=f"{OUT}/13-tablet-hero.png")
        await b.close()


asyncio.run(main())
print("\n".join(issues) if issues else "no console issues")
print("shots written to build/qa/")
