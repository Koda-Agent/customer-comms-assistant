#!/usr/bin/env python3
"""
Automated contact form submission using Playwright (headless)
"""

from playwright.sync_api import sync_playwright
import re

CONTACT_DATA = {
    "name": "Koda",
    "email": "koda-agent299@agentmail.to",
    "message": """Hi,

I'm Koda, building an AI assistant for service business customer communications.

I've developed a system that helps HVAC companies respond to customer emails faster and book more appointments automatically - even when you're on a job site.

Would love to show you a quick demo. What's the best email to send details?

Thanks,
Koda"""
}

def analyze_contact_page(url):
    """Analyze a contact page to find form fields"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Loading: {url}")
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")
        
        # Extract forms
        forms = page.query_selector_all("form")
        print(f"\nFound {len(forms)} form(s)")
        
        for i, form in enumerate(forms):
            print(f"\n=== Form {i+1} ===")
            
            # Find all input fields
            inputs = form.query_selector_all("input, textarea, select")
            for inp in inputs:
                tag = inp.evaluate("el => el.tagName")
                typ = inp.get_attribute("type") or ""
                name = inp.get_attribute("name") or ""
                placeholder = inp.get_attribute("placeholder") or ""
                id_attr = inp.get_attribute("id") or ""
                
                print(f"  {tag} type='{typ}' name='{name}' id='{id_attr}' placeholder='{placeholder}'")
            
            # Find submit button
            buttons = form.query_selector_all("button, input[type='submit']")
            for btn in buttons:
                tag = btn.evaluate("el => el.tagName")
                typ = btn.get_attribute("type") or ""
                text = btn.inner_text() if tag == "BUTTON" else btn.get_attribute("value")
                print(f"  SUBMIT: {tag} type='{typ}' text='{text}'")
        
        browser.close()

def submit_form(url, field_mappings):
    """Submit a contact form with given field mappings"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"\nSubmitting form to: {url}")
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")
        
        try:
            # Fill fields based on mappings
            for field_type, selector in field_mappings.items():
                value = CONTACT_DATA.get(field_type, "")
                if value:
                    print(f"  Filling {field_type}: {selector}")
                    page.fill(selector, value)
            
            # Submit
            submit_selector = field_mappings.get("submit")
            if submit_selector:
                print(f"  Clicking submit: {submit_selector}")
                page.click(submit_selector)
                page.wait_for_load_state("networkidle")
                
                # Check for success message
                success_indicators = ["thank you", "received", "we'll be in touch", "message sent"]
                page_text = page.inner_text("body").lower()
                
                if any(ind in page_text for ind in success_indicators):
                    print("  ✅ Form submitted successfully!")
                    browser.close()
                    return True
                else:
                    print("  ⚠️  Form submitted, but no clear success message")
                    browser.close()
                    return True
            else:
                print("  ❌ No submit button found")
                browser.close()
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            browser.close()
            return False

if __name__ == "__main__":
    # Analyze Brothers HVAC contact page
    print("=== Analyzing Contact Forms ===\n")
    analyze_contact_page("https://www.brothershvac.net/contact")
