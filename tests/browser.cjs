const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox']}); const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto((process.env.PH_TEST_URL || 'http://localhost:8765/ph-lernen-7k3q9x/') + '#/lernen');
 await page.waitForSelector('[data-option]');
 assert.equal(await page.locator('textarea').count(),0);
 assert.equal(await page.locator('#l-pruefen').isDisabled(),true);
 // A single choice replaces the previous selection without revealing the solution.
 await page.locator('[data-option]').nth(0).click();await page.locator('[data-option]').nth(1).click();
 assert.equal(await page.locator('[aria-pressed="true"]').count(),1);
 assert.equal(await page.locator('#l-aufloesung').innerText(),'');
 await page.locator('#l-pruefen').click();assert(await page.locator('#l-aufloesung').innerText());
 await page.waitForSelector('#l-bilder img');
 const image=page.locator('#l-bilder img').first();await image.evaluate(img=>img.decode());
 await page.locator('#l-abdeckung').click();await page.waitForSelector('#l-abdeckung-inhalt details');
 assert((await page.locator('#l-abdeckung-inhalt').innerText()).includes('Seiten mit Fragenbeleg'));
 await page.locator('#l-alle').click();await page.waitForSelector('#l-pruefen');
 // Inject a two-correct-choice fixture into the real learning UI.
 await page.evaluate(()=>{const q=sitzung.fragen[sitzung.schlange[sitzung.pos]];q.optionen=[{text:'A',richtig:true},{text:'B',richtig:false},{text:'C',richtig:true}];zeigeKarte();});
 assert((await page.locator('#l-typ').innerText()).includes('Multiple'));
 await page.locator('[data-option="0"]').click();await page.locator('#l-pruefen').click();
 assert((await page.locator('#l-aufloesung').innerText()).includes('Nicht richtig'));
 await page.evaluate(()=>zeigeKarte());
 await page.locator('[data-option="0"]').click();await page.locator('[data-option="2"]').click();
 assert.equal(await page.locator('[aria-pressed="true"]').count(),2);
 await page.locator('#l-pruefen').click();assert((await page.locator('#l-aufloesung').innerText()).startsWith('Richtig.'));
 // Mobile layout and image zoom.
 await page.setViewportSize({width:390,height:844});
 await page.locator('#l-bilder img').first().click();assert.equal(await page.locator('#zoom').isVisible(),true);
 await page.keyboard.press('Escape');assert.equal(await page.locator('#zoom').isVisible(),false);
 assert.deepEqual(errors,[]);
 console.log('Browser checks passed: selection, grading, images, coverage, all questions, mobile zoom.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
