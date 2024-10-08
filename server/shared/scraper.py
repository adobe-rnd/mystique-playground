from PIL import Image, ImageDraw
from io import BytesIO

from playwright.async_api import async_playwright

from server.shared.image import crop_and_downscale_image, image_to_bytes


class WebScraper:
    def __init__(self, headless=True):
        self.headless = headless

    async def get_html(self, url, selector="body", wait_time=0, consent_popup_button_selector=None):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            if wait_time > 0:
                print(f"Waiting for {wait_time}ms...")
                await page.wait_for_timeout(wait_time)

            if consent_popup_button_selector:
                await page.locator(consent_popup_button_selector).click()

            html = await page.locator(selector).inner_html()
            await browser.close()

            return html

    async def get_screenshot(self, url, selector="body", wait_time=0, consent_popup_button_selector=None):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            if wait_time > 0:
                print(f"Waiting for {wait_time}ms...")
                await page.wait_for_timeout(wait_time)

            if consent_popup_button_selector:
                try:
                    await page.locator(consent_popup_button_selector).click(timeout=10000)
                except Exception as e:
                    print("Consent popup button not found")

            screenshot_data = await page.locator(selector).first.screenshot()
            screenshot = Image.open(BytesIO(screenshot_data))

            await browser.close()

            return image_to_bytes(screenshot)

    async def get_html_and_screenshot(self, url, selector, with_styles=False, max_width=300, max_height=300, wait_time=0):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)

            page = await browser.new_page()

            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            if wait_time > 0:
                print(f"Waiting for {wait_time}ms...")
                await page.wait_for_timeout(wait_time)

            screenshot_data = await page.locator(selector).first.screenshot()
            screenshot = crop_and_downscale_image(screenshot_data, max_width, max_height)

            if not with_styles:
                html = await page.locator(selector).inner_html()
                await browser.close()

                return html, screenshot_data

            html_with_styles = await page.evaluate('''(selector) => {
            
                const essentialCssProperties = [
                    "color",
                    "background-color",
                    "background-image",
                    "background-size",
                    "font-family",
                    "font-size",
                    "font-weight",
                    "line-height",
                    "text-align",
                    "text-decoration",
                    "text-transform",
                    "display",
                    "position",
                    "top",
                    "right",
                    "bottom",
                    "left",
                    "float",
                    "clear",
                    "margin",
                    "padding",
                    "border",
                    "width",
                    "height",
                    "box-sizing",
                    "flex-direction",
                    "justify-content",
                    "align-items",
                    "flex-wrap",
                    "grid-template-columns",
                    "grid-template-rows",
                    "grid-gap",
                    "transition",
                    "animation",
                    "keyframes",
                    "transform",
                    "translate",
                    "rotate",
                    "scale",
                    "visibility",
                    "opacity",
                    "z-index",
                    "media queries"
                ];
            
                function getExplicitlySetStyles(element) {
                    const originalComputedStyle = window.getComputedStyle(element);
                    const explicitlySetStyles = {};
                    for (let property of originalComputedStyle) {
                        if (essentialCssProperties.includes(property)) {
                            explicitlySetStyles[property] = originalComputedStyle.getPropertyValue(property);
                        }
                    }
                    return explicitlySetStyles;
                }
    
                function applyInlineStyles(element) {
                    const styles = getExplicitlySetStyles(element);
                    for (let property in styles) {
                        element.style[property] = styles[property];
                    }
                    for (let child of element.children) {
                        applyInlineStyles(child);
                    }
                }
    
                const element = document.querySelector(selector);
                applyInlineStyles(element);
    
                return element.innerHTML;
                
            }''', selector)

            await browser.close()

            return html_with_styles, image_to_bytes(screenshot)

    async def get_full_page_screenshot_with_highlight(self, url, selector):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)

            page = await browser.new_page()

            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            element = await page.query_selector(selector)
            bbox = await element.bounding_box()

            await page.screenshot(path='screenshots/screenshot.png', full_page=True)
            await browser.close()

        # Open the screenshot and create a drawing context
        image = Image.open('screenshots/screenshot.png')
        draw = ImageDraw.Draw(image)

        # Draw a red rectangle around the desired section
        draw.rectangle(
            [
                (bbox['x'], bbox['y']),
                (bbox['x'] + bbox['width'], bbox['y'] + bbox['height'])
            ],
            outline='red',
            width=5
        )

        # Save the modified image
        image.save('screenshots/highlighted_screenshot.png')

        return image

    async def get_block_html(self, url, selector, wait_time=0):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            if wait_time > 0:
                print(f"Waiting for {wait_time}ms...")
                await page.wait_for_timeout(wait_time)

            # html = await page.locator(selector).inner_html()
            # Select the element and get its outer HTML
            html_element = await page.query_selector(selector)  # Replace 'selector' with your actual selector
            outer_html = await html_element.evaluate('element => element.outerHTML')
            await browser.close()

            return outer_html

    async def get_raw_css(self, url, selector):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            block_css, root_css_vars = await page.evaluate('''
                (selector) => {
                    const element = document.querySelector(selector);
                    if (!element) return null;

                    const blockName = element.dataset.blockName;
                    const stylesheets = Array.from(document.styleSheets);
                    const externalStyles = stylesheets.filter(sheet => sheet.href && sheet.ownerNode.nodeName === 'LINK');
                    const blockStyles = externalStyles.filter(sheet => sheet.href.includes(blockName)).map(sheet => {
                        try {
                            const rules = Array.from(sheet.cssRules).map(rule => rule.cssText);
                            return rules.join('\\n');
                        } catch (e) {
                            // Some stylesheets might be blocked due to CORS policies
                            console.error(`Could not access rules from stylesheet at ${sheet.href}`);
                            return [];
                        }
                    });

                    const rootStyles = externalStyles.filter(sheet => sheet.href.endsWith('/styles.css')).map(sheet => {
                        try {
                            const rules = Array.from(sheet.cssRules).map(rule => rule.cssText).filter(style => style.startsWith(':root'));
                            return rules[0];
                        } catch (e) {
                            // Some stylesheets might be blocked due to CORS policies
                            console.error(`Could not access rules from stylesheet at ${sheet.href}`);
                            return [];
                        }
                    });
                    return [blockStyles[0], rootStyles[0]];
                }
            ''', selector)

            await browser.close()

            return block_css, root_css_vars
