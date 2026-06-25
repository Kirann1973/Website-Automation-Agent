import asyncio
import logging
from playwright.async_api import Page
import tools
import config

# Setup logger for the agent
logger = logging.getLogger("agent")

async def find_form_element(page: Page, label_name: str, element_type: str = "input") -> str:
    """
    Finds a form element (input, textarea, etc.) using multiple resilient strategies.
    
    Strategies:
    1. ARIA/Label matching using Playwright's built-in accessibility/label mapping.
    2. Associated label ID lookup (via the 'for' attribute on the label).
    3. Placeholder text matching.
    4. Text search in nearby container siblings.
    
    Args:
        page (Page): The active Playwright page.
        label_name (str): The name/text of the label (e.g. "Username", "Description").
        element_type (str): The HTML tag type (e.g. "input", "textarea").
        
    Returns:
        str: A valid CSS selector to target the element.
    """
    logger.info("Searching for %s element labeled '%s'...", element_type, label_name)

    # Strategy 1: Look for labels with a 'for' attribute pointing to an ID
    labels = await page.query_selector_all("label")
    for label in labels:
        try:
            text = await label.inner_text()
            if label_name.lower() in text.lower():
                for_id = await label.get_attribute("for")
                if for_id:
                    # Escape colons which are common in generated IDs (e.g. :r3:-form-item)
                    escaped_id = for_id.replace(":", "\\:")
                    selector = f"#{escaped_id}"
                    # Verify the element exists
                    if await page.query_selector(selector):
                        logger.info("Found element via label 'for' attribute association: %s", selector)
                        return f"#{for_id}" # Playwright handles unescaped IDs in fill() when passed directly or using id=...
        except Exception as label_err:
            logger.debug("Error checking label: %s", label_err)

    # Strategy 2: Look for inputs/textareas inside a parent element containing the label text
    try:
        # Locate the label element
        label_el = await page.locator(f"label:has-text('{label_name}')").first
        if await label_el.count() > 0:
            # Find the input/textarea sibling or descendant of the parent
            parent = page.locator(f"div:has(label:has-text('{label_name}'))").first
            target = parent.locator(element_type).first
            if await target.count() > 0:
                # Retrieve ID to construct selector
                target_id = await target.get_attribute("id")
                if target_id:
                    logger.info("Found element in matching label container via ID: #%s", target_id)
                    return f"#{target_id}"
                
                # Check for name attribute
                target_name = await target.get_attribute("name")
                if target_name:
                    logger.info("Found element in matching label container via name: %s[name='%s']", element_type, target_name)
                    return f"{element_type}[name='{target_name}']"
    except Exception as container_err:
        logger.debug("Error checking container layout: %s", container_err)

    # Strategy 3: Target by placeholder variations if standard labels fail
    placeholders = {
        "username": ["shadcn", "username", "your name"],
        "description": ["description", "about", "bio", "tell us"]
    }
    
    key = label_name.lower()
    if key in placeholders:
        for placeholder in placeholders[key]:
            try:
                selector = f"{element_type}[placeholder*='{placeholder}']"
                if await page.query_selector(selector):
                    logger.info("Found element via placeholder match: %s", selector)
                    return selector
            except Exception as ph_err:
                logger.debug("Error checking placeholder '%s': %s", placeholder, ph_err)

    # Strategy 4: Fallback attribute match
    try:
        selector = f"{element_type}[name*='{key}']"
        if await page.query_selector(selector):
            logger.info("Found element via fallback name attribute: %s", selector)
            return selector
    except Exception as name_err:
        logger.debug("Error checking name fallback: %s", name_err)

    raise ValueError(f"Could not locate form element for label '{label_name}' using any strategy.")

async def run_agent():
    target_url = "https://ui.shadcn.com/docs/forms/react-hook-form"
    logger.info("Initializing Agent Workflow...")

    try:
        # Step 1: Open browser (headless is configurable via config or default to False)
        page = await tools.open_browser(headless=config.HEADLESS)

        # Step 2: Navigate to target URL
        await tools.Maps_to_url(target_url)
        await asyncio.sleep(2) # Give a moment for client-side rendering

        # Step 3: Scroll the form into view if necessary
        # Shadcn forms on documentation pages are usually in the page body, let's scroll down slightly to ensure visibility
        logger.info("Scrolling down to ensure form elements are visible...")
        await tools.scroll("down", 350)
        await asyncio.sleep(1)

        # Step 4: Dynamically locate Username/Name field and input text
        # On this Shadcn page, the field is labeled "Username" and has placeholder "shadcn"
        username_selector = await find_form_element(page, "Username", "input")
        await tools.type_text(username_selector, "Antigravity Agent")
        await asyncio.sleep(1)

        # Step 5: Dynamically locate Description field and input text
        # Shadcn page preview has a Bio/Description text field, or let's try finding the form submission button
        # Wait, let's see if there is another input field or textarea (e.g. Description, Email)
        # In react-hook-form docs, there is often a Username field and sometimes other fields like Email or Bio.
        # Let's dynamically locate "Email" or "Bio" or "Description" textareas/inputs if they exist, or handle gracefully.
        try:
            desc_selector = await find_form_element(page, "Description", "textarea")
            await tools.type_text(desc_selector, "This is an automated description generated by the university website automation agent project.")
        except Exception as desc_exc:
            logger.warning("Could not find a 'Description' textarea. Let's try searching for any textarea or description inputs: %s", desc_exc)
            # Try finding any textarea on page
            textarea_count = await page.locator("textarea").count()
            if textarea_count > 0:
                await tools.type_text("textarea", "Default bio description filled by the automation agent.")
            else:
                logger.info("No description textareas found. Proceeding with screenshot.")

        await asyncio.sleep(1)

        # Step 6: Take success screenshot
        screenshot_name = "shadcn_form_success.png"
        screenshot_path = await tools.take_screenshot(screenshot_name)
        logger.info("Orchestration completed successfully. Success screenshot saved to %s", screenshot_path)

    except Exception as e:
        logger.error("Agent workflow execution failed: %s", e, exc_info=True)
    finally:
        # Step 7: Clean up browser session
        await tools.close_browser()

if __name__ == "__main__":
    # Ensure config logging is ready
    config.setup_logging()
    asyncio.run(run_agent())
