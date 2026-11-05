"""Screenshot + interaction QA across home, project, and legal pages."""
import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
URL = "file://" + os.path.join(ROOT, "gitguild", "index.html")
LEGAL = "file://" + os.path.join(ROOT, "gitguild", "legal", "privacy.html")
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
        first_id, last_id = await p.evaluate("[window.GUILD.order[0], window.GUILD.order[Math.min(6, window.GUILD.order.length - 1)]]")
        project_page = "file://" + os.path.join(ROOT, "gitguild", (await p.evaluate("id => window.GuildEmblem.pageUrl(id)", first_id)))
        await p.screenshot(path=f"{OUT}/01-hero.png")

        n = p.locator(f'.node[data-id="{first_id}"]')
        await n.hover()
        await p.wait_for_timeout(650)
        await p.screenshot(path=f"{OUT}/02-hover-node.png")

        # Node click selects in place, synchronizing the spotlight.
        await n.click()
        await p.wait_for_timeout(900)
        issues.append(f"node click selects (stays home) -> {p.url}")
        await p.screenshot(path=f"{OUT}/03-selected.png")
        await p.goto(URL)
        await p.wait_for_timeout(3200)

        # select-only ring + chip jumps to the work section
        await p.evaluate("window.scrollTo(0,0)")
        await p.wait_for_timeout(400)
        await p.locator(f'.node[data-id="{last_id}"]').click()
        await p.wait_for_timeout(700)
        await p.screenshot(path=f"{OUT}/03b-chip.png")
        await p.locator(".sel-chip").click()
        await p.wait_for_timeout(1200)
        await p.screenshot(path=f"{OUT}/03c-chip-work.png")
        await p.keyboard.press("Escape")
        await p.wait_for_timeout(500)

        await p.evaluate("location.hash = '#work'")
        await p.wait_for_timeout(900)
        await p.screenshot(path=f"{OUT}/04-slider.png")

        await p.locator(".sidx__row").nth(4).hover()
        await p.wait_for_timeout(500)
        await p.screenshot(path=f"{OUT}/05-index-hover.png")

        await p.evaluate("document.getElementById('train-title').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(800)
        await p.locator(".commit").nth(3).hover()
        await p.wait_for_timeout(500)
        await p.screenshot(path=f"{OUT}/06-train.png")

        await p.evaluate("document.getElementById('join').scrollIntoView({block:'center'})")
        await p.wait_for_timeout(800)
        await p.screenshot(path=f"{OUT}/07-join.png")

        await p.evaluate("document.getElementById('manifesto').scrollIntoView({block:'start'})")
        await p.wait_for_timeout(700)
        await p.screenshot(path=f"{OUT}/07b-manifesto.png")

        await p.evaluate("document.querySelector('.footer').scrollIntoView({block:'end'})")
        await p.wait_for_timeout(700)
        await p.screenshot(path=f"{OUT}/07c-footer.png")

        await p.goto(project_page)
        await p.wait_for_timeout(900)
        await p.screenshot(path=f"{OUT}/07d-project.png")
        await p.goto(LEGAL)
        await p.wait_for_timeout(700)
        await p.screenshot(path=f"{OUT}/07e-legal.png")

        await p.goto(URL)
        await p.wait_for_timeout(2000)
        await p.evaluate("""async () => {
          const step = Math.max(320, Math.floor(innerHeight * 0.8));
          for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
            scrollTo(0, y);
            await new Promise(resolve => setTimeout(resolve, 70));
          }
          scrollTo(0, 0);
        }""")
        await p.wait_for_timeout(500)
        await p.screenshot(path=f"{OUT}/08-full.png", full_page=True)

        # mobile
        m = await b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        m.on("pageerror", lambda e: issues.append(f"[mobile] pageerror: {e}"))
        await m.goto(URL)
        await m.wait_for_timeout(3200)
        await m.screenshot(path=f"{OUT}/09-mobile-hero.png")
        await m.locator(f'.node[data-id="{last_id}"]').tap()
        await m.wait_for_timeout(1200)
        issues.append(f"[mobile] node tap selects (stays home) -> {m.url}")
        await m.screenshot(path=f"{OUT}/10-mobile-chip.png")
        await m.locator(".sel-chip").tap()
        await m.wait_for_timeout(1200)
        await m.screenshot(path=f"{OUT}/10b-mobile-work.png")
        await m.goto(URL)
        await m.wait_for_timeout(3000)
        await m.locator("#work").scroll_into_view_if_needed()
        await m.wait_for_timeout(700)
        await m.screenshot(path=f"{OUT}/11-mobile-slider.png")
        await m.evaluate("document.getElementById('train-title').scrollIntoView({block:'start'})")
        await m.wait_for_timeout(700)
        await m.screenshot(path=f"{OUT}/12-mobile-train.png")

        # tablet
        t = await b.new_page(viewport={"width": 820, "height": 1100})
        await t.goto(URL)
        await t.wait_for_timeout(3000)
        await t.screenshot(path=f"{OUT}/13-tablet-hero.png")
        await t.goto(project_page)
        await t.wait_for_timeout(900)
        await t.screenshot(path=f"{OUT}/14-tablet-project.png")
        await b.close()


asyncio.run(main())
print("\n".join(issues) if issues else "no console issues")
print("shots written to build/qa/")
