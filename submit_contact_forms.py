#!/usr/bin/env python3
"""
Automated contact form submission using Playwright
Submits inquiries to target businesses to get email addresses
"""

import sys
from playwright.sync_api import sync_playwright
import time

# Contact form data
CONTACT_DATA = {
    "name": "Koda",
    "email": "koda-agent299@agentmail.to",
    "phone": "",  # Leave blank
    "message": """Hi,

I'm Koda, building an AI assistant for service business customer communications.

I've developed a system that helps HVAC companies respond to customer emails faster and book more appointments automatically - even when you're on a job site.

Would love to show you a quick demo. What's the best email to send details?

Thanks,
Koda"""
}

def submit_brothers_hvac():
    """Submit contact form to Brothers HVAC"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("Opening Brothers HVAC contact page...")
            page.goto("https://www.brothershvac.net/contact", timeout=30000)
            
            print("Filling form...")
            # This is a placeholder - need to inspect actual form fields
            # Would need to run with headless=False first to see the form structure
            
            # Common patterns:
            # page.fill('input[name="name"]', CONTACT_DATA["name"])
            # page.fill('input[name="email"]', CONTACT_DATA["email"])
            # page.fill('textarea[name="message"]', CONTACT_DATA["message"])
            # page.click('button[type="submit"]')
            
            print("Form structure:")
            print(page.content())
            
            time.sleep(2)
            browser.close()
            return True
            
        except Exception as e:
            print(f"Error: {e}")
            browser.close()
            return False

def test_form_detection():
    """Test: detect form fields on contact page"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Run in headed mode to see
        page = browser.new_page()
        
        print("Loading Brothers HVAC contact page...")
        page.goto("https://www.brothershvac.net/contact", timeout=30000)
        
        print("\nSearching for form fields...")
        
        # Try to find common form field patterns
        selectors_to_try = [
            'input[type="text"]',
            'input[type="email"]',
            'textarea',
            'input[name*="name"]',
            'input[name*="email"]',
            'input[name*="phone"]',
            'textarea[name*="message"]',
            'button[type="submit"]',
            'input[type="submit"]',
        ]
        
        for selector in selectors_to_try:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"  Found {len(elements)} element(s) matching: {selector}")
                for i, el in enumerate(elements):
                    name = el.get_attribute('name') or ''
                    placeholder = el.get_attribute('placeholder') or ''
                    print(f"    [{i}] name='{name}' placeholder='{placeholder}'")
        
        print("\nPage loaded. Press Ctrl+C to close...")
        time.sleep(30)  # Keep open for inspection
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running in test/inspection mode...")
        test_form_detection()
    else:
        print("Submitting contact form...")
        submit_brothers_hvac()
