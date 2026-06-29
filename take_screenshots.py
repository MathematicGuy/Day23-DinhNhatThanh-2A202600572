"""Playwright-based automated screenshot capture script.

Visits running localhost dashboards and captures actual visual evidence.
"""
from __future__ import annotations

import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # 1. Overview Dashboard
        print("Capturing dashboard-overview.png...")
        try:
            await page.goto("http://localhost:3000/d/day23-ai-overview/ai-service-overview-day-23?orgId=1&kiosk", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(10)  # Wait for Grafana queries to render
            await page.screenshot(path="submission/screenshots/dashboard-overview.png")
            print("Successfully captured dashboard-overview.png")
        except Exception as e:
            print("Failed to capture dashboard-overview.png:", e)

        # 2. SLO Burn Rate Dashboard
        print("Capturing slo-burn-rate.png...")
        try:
            await page.goto("http://localhost:3000/d/day23-slo/slo-burn-rate-day-23?orgId=1&kiosk", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(10)
            await page.screenshot(path="submission/screenshots/slo-burn-rate.png")
            print("Successfully captured slo-burn-rate.png")
        except Exception as e:
            print("Failed to capture slo-burn-rate.png:", e)

        # 3. Cross-Day Dashboard
        print("Capturing cross-day-dashboard.png...")
        try:
            await page.goto("http://localhost:3000/d/day23-cross-day/cross-day-stack-day-23-integrative?orgId=1&kiosk", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(10)
            await page.screenshot(path="submission/screenshots/cross-day-dashboard.png")
            print("Successfully captured cross-day-dashboard.png")
        except Exception as e:
            print("Failed to capture cross-day-dashboard.png:", e)

        # 4. Jaeger Trace
        print("Capturing jaeger-trace.png...")
        try:
            await page.goto("http://localhost:16686/trace/af040211e588abcc68cbb418ef05abf6", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(6)
            await page.screenshot(path="submission/screenshots/jaeger-trace.png")
            print("Successfully captured jaeger-trace.png")
        except Exception as e:
            print("Failed to capture jaeger-trace.png:", e)

        # 5. Jaeger Attrs
        print("Capturing jaeger-attrs.png...")
        try:
            await page.goto("http://localhost:16686/trace/af040211e588abcc68cbb418ef05abf6", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(6)
            # Try to click the first span row to show attributes panel
            span_header = await page.query_selector(".span-view")
            if span_header:
                await span_header.click()
                await asyncio.sleep(2)
            await page.screenshot(path="submission/screenshots/jaeger-attrs.png")
            print("Successfully captured jaeger-attrs.png")
        except Exception as e:
            print("Failed to capture jaeger-attrs.png:", e)

        # 6. AgentOps Jaeger
        print("Capturing agentops-jaeger.png...")
        try:
            await page.goto("http://localhost:16686/trace/f41e0b4a33773302e21b73b55646846f", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(6)
            await page.screenshot(path="submission/screenshots/agentops-jaeger.png")
            print("Successfully captured agentops-jaeger.png")
        except Exception as e:
            print("Failed to capture agentops-jaeger.png:", e)

        # 7. Alertmanager
        print("Capturing alertmanager-firing.png...")
        try:
            await page.goto("http://localhost:9093", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(6)
            await page.screenshot(path="submission/screenshots/alertmanager-firing.png")
            print("Successfully captured alertmanager-firing.png")
        except Exception as e:
            print("Failed to capture alertmanager-firing.png:", e)

        # 8. Pyroscope / Flame Graph
        print("Capturing flamegraph.png...")
        try:
            await page.goto("http://localhost:4040", wait_until="networkidle", timeout=15000)
            await asyncio.sleep(6)
            await page.screenshot(path="submission/screenshots/flamegraph.png")
            print("Successfully captured flamegraph.png")
        except Exception as e:
            print("Failed to capture flamegraph.png:", e)

        await browser.close()
        print("All automated screenshots capture complete!")


if __name__ == "__main__":
    asyncio.run(run())
