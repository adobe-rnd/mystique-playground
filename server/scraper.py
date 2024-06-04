from playwright.async_api import async_playwright


class WebScraper:
    def __init__(self, headless=True):
        self.headless = headless

    async def get_html_and_screenshot(self, url, selector, with_styles=False):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)

            page = await browser.new_page()

            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            screenshot_data = await page.locator(selector).screenshot()

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

            return html_with_styles, screenshot_data
