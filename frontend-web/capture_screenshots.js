import puppeteer from 'puppeteer';
import * as path from 'path';

(async () => {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Go to the local web app
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });

    const captureDir = path.join(process.cwd(), '../play_store_assets');

    // Phone 1 - Login Screen
    await page.setViewport({ width: 1080, height: 1920, isMobile: true, hasTouch: true });
    await page.screenshot({ path: path.join(captureDir, 'phone_1.png') });

    // Tablet 7-inch - Login Screen
    await page.setViewport({ width: 1200, height: 1920, isMobile: true, hasTouch: true });
    await page.screenshot({ path: path.join(captureDir, 'tablet7_1.png') });

    // Tablet 10-inch - Login Screen
    await page.setViewport({ width: 1600, height: 2560, isMobile: true, hasTouch: true });
    await page.screenshot({ path: path.join(captureDir, 'tablet10_1.png') });

    // Now let's try to just change something on the page (like a state) or take another screenshot
    // Click on "Register" tab if available, or just scroll down to get a second screenshot

    try {
        // Look for registration toggle
        const toggleButtons = await page.$$('button');
        for (const btn of toggleButtons) {
            const text = await page.evaluate(el => el.textContent, btn);
            if (text && text.includes('Sign Up')) {
                await btn.click();
                await new Promise(r => setTimeout(r, 1000));
                break;
            }
        }
    } catch (e) {
        console.log("No toggle button found");
    }

    // Phone 2 - Signup or scrolled state
    await page.setViewport({ width: 1080, height: 1920, isMobile: true, hasTouch: true });
    await page.screenshot({ path: path.join(captureDir, 'phone_2.png') });

    // Tablet 7-inch 2
    await page.setViewport({ width: 1200, height: 1920, isMobile: true, hasTouch: true });
    await page.screenshot({ path: path.join(captureDir, 'tablet7_2.png') });

    // Tablet 10-inch 2
    await page.setViewport({ width: 1600, height: 2560, isMobile: true, hasTouch: true });
    await page.screenshot({ path: path.join(captureDir, 'tablet10_2.png') });

    await browser.close();
    console.log('Screenshots captured successfully!');
})();
