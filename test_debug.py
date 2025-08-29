#!/usr/bin/env python3
"""
Debug why temple data isn't loading on GitHub Pages
"""

import time
from playwright.sync_api import sync_playwright

def debug_site():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Set up console message listener
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        
        # Set up response listener
        responses = []
        page.on("response", lambda response: responses.append({
            "url": response.url,
            "status": response.status,
            "ok": response.ok
        }))
        
        print("🔍 Debugging Temple App...")
        print("=" * 50)
        
        # Navigate to the page
        page.goto("https://petchiraj.github.io/tamil-temple-calendar/", wait_until='networkidle')
        time.sleep(5)
        
        print("\n📊 Network Requests:")
        for resp in responses:
            if 'temple_data' in resp['url'] or resp['status'] != 200:
                status_emoji = "✅" if resp['ok'] else "❌"
                print(f"{status_emoji} {resp['status']} - {resp['url']}")
        
        print("\n📝 Console Messages:")
        for msg in console_messages:
            if 'error' in msg.lower() or 'failed' in msg.lower():
                print(f"   {msg}")
        
        # Check if temples loaded
        temples_data = page.evaluate('''() => {
            return {
                templesCount: window.AppState ? window.AppState.temples.length : 0,
                errorState: document.querySelector('.error-message')?.innerText || null,
                loadingVisible: document.querySelector('.loading-spinner')?.style.display !== 'none'
            }
        }''')
        
        print(f"\n📈 App State:")
        print(f"   Temples loaded: {temples_data['templesCount']}")
        print(f"   Error message: {temples_data['errorState']}")
        print(f"   Still loading: {temples_data['loadingVisible']}")
        
        # Take screenshot
        page.screenshot(path="debug_screenshot.png")
        print("\n📸 Screenshot saved as 'debug_screenshot.png'")
        
        browser.close()

if __name__ == "__main__":
    debug_site()