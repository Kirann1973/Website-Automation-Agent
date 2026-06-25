import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
import config

logger = logging.getLogger("tools")

class BrowserStateManager:
    """
    Manages the global state of the Playwright browser instance, context, and active page.
    This allows helper functions to easily access the active browser session.
    """
    def __init__(self):
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def close_all(self):
        """Closes all active resources and resets the state."""
        logger.info("Cleaning up and closing browser resources...")
        if self.page:
            try:
                await self.page.close()
                logger.info("Page closed successfully.")
            except Exception as e:
                logger.error("Error closing page: %s", e)
            self.page = None

        if self.context:
            try:
                await self.context.close()
                logger.info("Browser context closed successfully.")
            except Exception as e:
                logger.error("Error closing context: %s", e)
            self.context = None

        if self.browser:
            try:
                await self.browser.close()
                logger.info("Browser closed successfully.")
            except Exception as e:
                logger.error("Error closing browser: %s", e)
            self.browser = None

        if self.playwright:
            try:
                await self.playwright.stop()
                logger.info("Playwright engine stopped.")
            except Exception as e:
                logger.error("Error stopping Playwright: %s", e)
            self.playwright = None

# Global instance to store browser state across tool execution
state = BrowserStateManager()

async def open_browser(headless: bool = False) -> Page:
    """
    Launches a Chromium browser, creates a new browser context and a new page,
    and updates the global state.

    Args:
        headless (bool): Whether to run the browser in headless mode. Defaults to False.

    Returns:
        Page: The newly created Playwright Page object.
    """
    logger.info("Initializing Playwright and launching Chromium (headless=%s)...", headless)
    try:
        # Clean up any existing session before opening a new one
        await state.close_all()

        state.playwright = await async_playwright().start()
        state.browser = await state.playwright.chromium.launch(
            headless=headless,
            args=["--start-maximized"]
        )
        
        # Create a new browser context with viewport size matching common screen
        state.context = await state.browser.new_context(
            no_viewport=True  # Allows the browser to maximize based on '--start-maximized'
        )
        
        # Set default timeout from configuration
        state.context.set_default_timeout(config.DEFAULT_TIMEOUT)
        
        state.page = await state.context.new_page()
        logger.info("Browser launched and new page opened successfully.")
        return state.page
    except Exception as e:
        logger.error("Failed to launch browser: %s", e, exc_info=True)
        # Attempt cleanup on failure
        await state.close_all()
        raise e

async def Maps_to_url(url: str) -> None:
    """
    Navigates the current browser page to the specified URL and waits for network idle state.

    Args:
        url (str): The destination URL.
    """
    if not state.page:
        logger.error("Navigation failed: No active page. Call open_browser() first.")
        raise RuntimeError("Browser not open. Call open_browser() before navigating.")

    logger.info("Navigating to URL: %s", url)
    try:
        # Navigate and wait until there are no network connections for at least 500 ms
        response = await state.page.goto(url, wait_until="networkidle")
        status = response.status if response else "Unknown"
        logger.info("Successfully navigated to %s. Response status: %s", url, status)
    except Exception as e:
        logger.error("Error navigating to %s: %s", url, e, exc_info=True)
        raise e

async def take_screenshot(filename: str) -> str:
    """
    Saves a screenshot of the current page viewport.

    Args:
        filename (str): The filename for the screenshot (e.g. 'homepage.png').

    Returns:
        str: The absolute file path of the saved screenshot.
    """
    if not state.page:
        logger.error("Screenshot failed: No active page.")
        raise RuntimeError("Browser not open. Call open_browser() before taking a screenshot.")

    # Determine full destination path
    screenshot_path = config.SCREENSHOT_DIR / filename
    logger.info("Taking screenshot and saving to: %s", screenshot_path)
    try:
        await state.page.screenshot(path=str(screenshot_path))
        logger.info("Screenshot successfully saved to %s", screenshot_path)
        return str(screenshot_path)
    except Exception as e:
        logger.error("Failed to capture screenshot: %s", e, exc_info=True)
        raise e

async def click_on_screen(x: int, y: int) -> None:
    """
    Performs a click action at the exact (x, y) pixel coordinates on the screen/page.

    Args:
        x (int): The horizontal coordinate.
        y (int): The vertical coordinate.
    """
    if not state.page:
        logger.error("Click failed: No active page.")
        raise RuntimeError("Browser not open. Call open_browser() before clicking.")

    logger.info("Performing click at coordinates: (x=%d, y=%d)", x, y)
    try:
        await state.page.mouse.click(x, y)
        logger.info("Click executed successfully at (x=%d, y=%d)", x, y)
    except Exception as e:
        logger.error("Failed to click at coordinates (x=%d, y=%d): %s", x, y, e, exc_info=True)
        raise e

async def send_keys(selector: str, text: str) -> None:
    """
    Inputs text into a target element matching the given selector.
    Clears any existing content in the element first.

    Args:
        selector (str): The CSS selector or Playwright selector for the target element.
        text (str): The text string to input.
    """
    if not state.page:
        logger.error("Send keys failed: No active page.")
        raise RuntimeError("Browser not open. Call open_browser() before sending keys.")

    logger.info("Sending keys/text to element '%s'. Text length: %d characters", selector, len(text))
    try:
        # Wait for the selector to be attached/visible
        await state.page.wait_for_selector(selector, state="visible")
        # Click the element to focus it
        await state.page.click(selector)
        # Clear existing text using fill or keyboard commands if needed; fill handles it directly
        await state.page.fill(selector, text)
        logger.info("Successfully filled element '%s' with text.", selector)
    except Exception as e:
        logger.error("Failed to send keys to element '%s': %s", selector, e, exc_info=True)
        raise e

async def type_text(selector: str, text: str) -> None:
    """
    Alias for send_keys to provide flexible naming. Inputs text into a target element.
    """
    logger.info("Alias type_text called for selector '%s'. delegating to send_keys.", selector)
    await send_keys(selector, text)

async def scroll(direction: str, amount: int) -> None:
    """
    Scrolls the viewport page up or down by a specific pixel amount.

    Args:
        direction (str): Must be 'up' or 'down'.
        amount (int): The number of pixels to scroll.
    """
    if not state.page:
        logger.error("Scroll failed: No active page.")
        raise RuntimeError("Browser not open. Call open_browser() before scrolling.")

    direction = direction.lower().strip()
    if direction not in ("up", "down"):
        logger.error("Scroll failed: Invalid direction '%s'. Must be 'up' or 'down'.", direction)
        raise ValueError("Direction must be either 'up' or 'down'.")

    # Determine scroll delta
    scroll_y = -amount if direction == "up" else amount
    logger.info("Scrolling page %s by %d pixels.", direction, amount)

    try:
        await state.page.evaluate(f"window.scrollBy(0, {scroll_y})")
        logger.info("Scroll action executed successfully.")
    except Exception as e:
        logger.error("Failed to scroll page: %s", e, exc_info=True)
        raise e

async def double_click(selector: str) -> None:
    """
    Performs a double-click on a target element matching the given selector.

    Args:
        selector (str): The selector for the target element.
    """
    if not state.page:
        logger.error("Double click failed: No active page.")
        raise RuntimeError("Browser not open. Call open_browser() before double clicking.")

    logger.info("Performing double click on element: '%s'", selector)
    try:
        await state.page.wait_for_selector(selector, state="visible")
        await state.page.dblclick(selector)
        logger.info("Double click executed successfully on element '%s'.", selector)
    except Exception as e:
        logger.error("Failed to double click on element '%s': %s", selector, e, exc_info=True)
        raise e

async def close_browser() -> None:
    """
    Explicitly closes the browser and cleans up state resources.
    """
    logger.info("Explicit request received to close browser.")
    await state.close_all()
