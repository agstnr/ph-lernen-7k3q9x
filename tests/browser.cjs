const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',args:['--no-sandbox']});
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto((process.env.PH_TEST_URL||'http://localhost:8765/ph-lernen-7k3q9x/')+'#/lernen');await page.waitForSelector('[data-option]');
 const show=async(mode,graphics)=>page.evaluate(({mode,graphics})=>{
  const q=Object.values(sitzung.fragen).find(q=>q.modus===mode && (q.grafiken.length>0)===graphics);
  if(!q)throw Error('Missing test question');sitzung.schlange=[q.id];sitzung.pos=0;zeigeKarte();
  return {id:q.id,correct:q.optionen.flatMap((o,i)=>o.richtig?[i]:[]),wrong:q.optionen.findIndex(o=>!o.richtig)};
 },{mode,graphics});
 const choose=async(i)=>page.locator(`[data-option="${i}"]`).click();
 const submit=async()=>page.locator('#l-pruefen').click();
 // Real text-only question: no full slide fallback, and changing a single answer is allowed.
 let q=await show('single',false);assert.equal(await page.locator('textarea').count(),0);assert.equal(await page.locator('#l-bilder img').count(),0);
 assert(await page.locator('#l-pruefen').isDisabled());await choose(q.wrong);await choose(q.correct[0]);
 assert.equal(await page.locator('[aria-pressed="true"]').count(),1);assert.equal(await page.locator('#l-aufloesung').innerText(),'');await submit();
 assert((await page.locator('#l-aufloesung').innerText()).startsWith('Richtig.'));
 // A real multiple-choice question must reject an incomplete answer and an extra wrong answer.
 q=await show('multiple',false);await choose(q.correct[0]);await submit();assert((await page.locator('#l-aufloesung').innerText()).startsWith('Nicht richtig.'));
 q=await show('multiple',false);for(const i of q.correct)await choose(i);await choose(q.wrong);await submit();assert((await page.locator('#l-aufloesung').innerText()).startsWith('Nicht richtig.'));
 q=await show('multiple',false);for(const i of q.correct)await choose(i);await submit();assert((await page.locator('#l-aufloesung').innerText()).startsWith('Richtig.'));
 // Only the explicitly assigned diagram crops load; verify mobile keyboard zoom.
 await show('single',true);const image=page.locator('#l-bilder img').first();assert((await image.getAttribute('src')).includes('/daten/grafiken/'));await image.evaluate(img=>img.decode());
 await page.setViewportSize({width:390,height:844});await image.focus();await page.keyboard.press('Enter');assert(await page.locator('#zoom').isVisible());await page.keyboard.press('Escape');assert.equal(await page.locator('#zoom').isVisible(),false);
 await page.locator('#l-abdeckung').click();await page.waitForSelector('#l-abdeckung-inhalt details');const coverage=await page.locator('#l-abdeckung-inhalt').innerText();assert(coverage.includes('Seiten mit Fragenbeleg'));assert(!coverage.includes('Lückentext'));
 await page.locator('#l-alle').click();const totals=await page.evaluate(()=>({selected:sitzung.auswahl.length,queue:sitzung.schlange.length}));assert.equal(totals.selected,totals.queue);assert(totals.queue>2000);
 await page.screenshot({path:'/workspace/work/learning-mobile.png',fullPage:true});assert.deepEqual(errors,[]);
 console.log('Browser passed: real single/multiple questions, complete-set grading, no full-slide fallback, cropped diagrams, keyboard/mobile zoom, coverage, unrestricted full round.');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
