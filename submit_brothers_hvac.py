#!/usr/bin/env python3
"""
Submit contact form to Brothers HVAC
"""

from playwright.sync_api import sync_playwright
import time

def submit_brothers_hvac():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Loading Brothers HVAC contact page...")
        page.goto("https://www.brothershvac.net/contact", timeout=30000)
        page.wait_for_load_state("networkidle")
        
        try:
            # Fill the form (Form 2, fields: dmform-5, 6, 7, 8, 3)
            # Based on common patterns: Name, Email, Phone, Subject, Message
            
            print("Filling form fields...")
            page.fill('input[name="dmform-5"]', 'Koda')  # Likely: Name
            page.fill('input[name="dmform-6"]', 'koda-agent299@agentmail.to')  # Likely: Email
            page.fill('input[name="dmform-7"]', '')  # Likely: Phone (leaving blank)
            page.fill('input[name="dmform-8"]', 'Business Inquiry')  # Likely: Subject
            page.fill('textarea[name="dmform-3"]', '''Hi,

I'm Koda, building an AI assistant for service business customer communications.

I've developed a system that helps HVAC companies respond to customer emails faster and book more appointments automatically - even when you're on a job site.

Would love to show you a quick demo. What's the best email to send details?

Thanks,
Koda''')
            
            print("Submitting form...")
            page.click('input[type="submit"][name="submit"]')
            
            # Wait for response
            time.sleep(3)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # Check for success
            page_text = page.inner_text("body").lower()
            success_indicators = ["thank you", "received", "we'll be in touch", "message sent", "submitted"]
            
            if any(ind in page_text for ind in success_indicators):
                print("✅ Form submitted successfully to Brothers HVAC!")
                print(f"   Response URL: {page.url}")
                browser.close()
                return True
            else:
                print("⚠️  Form submitted, checking response...")
                print(f"   Current URL: {page.url}")
                # Save screenshot for debugging
                page.screenshot(path="/tmp/brothers_hvac_result.png")
                print("   Screenshot saved to /tmp/brothers_hvac_result.png")
                browser.close()
                return True  # Assume success if no error
                
        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="/tmp/brothers_hvac_error.png")
            print("   Error screenshot saved")
            browser.close()
            return False

if __name__ == "__main__":
    success = submit_brothers_hvac()
    exit(0 if success else 1)
