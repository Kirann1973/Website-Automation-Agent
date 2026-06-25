import asyncio
import logging
from pathlib import Path
import tools

logger = logging.getLogger("verifier")

async def main():
    logger.info("Starting website automation verification test...")

    # Define paths
    test_page_path = Path(__file__).resolve().parent / "test_page.html"
    file_url = f"file://{test_page_path}"

    try:
        # 1. Open the browser (headless=False as requested)
        page = await tools.open_browser(headless=False)

        # 2. Navigate to the local test HTML page
        await tools.Maps_to_url(file_url)
        await asyncio.sleep(1)

        # 3. Type text into the text input box
        await tools.type_text("#text-input", "Hello University Project!")
        await asyncio.sleep(1)

        # 4. Double click the double-click button
        await tools.double_click("#dbl-click-btn")
        await asyncio.sleep(1)

        # 5. Click on screen: let's click the Click Me button.
        # We can locate the button's position dynamically to make coordinates accurate
        btn_selector = "#click-btn"
        element = await page.wait_for_selector(btn_selector)
        box = await element.bounding_box()
        if box:
            # Click at center of the button bounding box
            x = int(box["x"] + box["width"] / 2)
            y = int(box["y"] + box["height"] / 2)
            await tools.click_on_screen(x, y)
        else:
            logger.warning("Could not retrieve bounding box for button. Defaulting click to (100, 200)")
            await tools.click_on_screen(100, 200)
        await asyncio.sleep(1)

        # 6. Scroll down by 800 pixels
        await tools.scroll("down", 800)
        await asyncio.sleep(1)

        # 7. Take screenshot
        screenshot_path = await tools.take_screenshot("test_verification.png")
        logger.info("Screenshot taken successfully: %s", screenshot_path)

        # 8. Scroll back up by 400 pixels
        await tools.scroll("up", 400)
        await asyncio.sleep(1)

        logger.info("All automation tools verified successfully!")

    except Exception as e:
        logger.error("Verification failed with exception: %s", e, exc_info=True)
    finally:
        # Cleanup browser resources
        await tools.close_browser()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
