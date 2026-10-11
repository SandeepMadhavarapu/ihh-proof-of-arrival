import { chromium } from 'playwright';
const U='http://127.0.0.1:8731/verify.html';
const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const pass=[],fail=[];
const ck=(c,m)=>(c?pass:fail).push(m);

/* ── 1. with JavaScript ─────────────────────────────────────────── */
let ctx=await b.newContext({viewport:{width:1280,height:900}});
let p=await ctx.newPage();
const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto(U,{waitUntil:'load'});

/* Counts are derived from the rendered page, not hardcoded: a stale literal here
   is what failed when the case files were rewritten. The invariants below are the
   real contract — every claim has a drawer, controls scale with the data. */
const N = {
  claims:  await p.locator('.cl').count(),
  drawers: await p.locator('.cl .ev').count(),
  evidence:await p.locator('.cl .ev-item').count(),
};
ck(N.claims >= 15, N.claims+' claims rendered (15+ expected)');
ck(N.drawers === N.claims, 'every one of the '+N.claims+' claims has an evidence drawer');
ck(N.evidence >= N.claims, N.evidence+' evidence items across '+N.claims+' claims');
ck((await p.locator('.cur[open]').count())===0, 'curator findings start closed');
ck((await p.textContent('#done'))==='0', 'tally starts at 0');
ck((await p.textContent('#sheet-body')).includes('No findings recorded'), 'sheet starts empty');

/* keyboard: focus the first radio and choose with the keyboard only */
const first = p.locator('#h1 input[type=radio]').first();
await first.focus();
ck(await p.evaluate(()=>document.activeElement.type==='radio'), 'first verdict control is focusable');
await p.keyboard.press('ArrowDown');            // radio group: move to "Not supported"
await p.keyboard.press('ArrowDown');            // -> "Contradicted"
const picked = await p.evaluate(()=>document.querySelector('#h1 input:checked')?.value);
ck(picked==='contradicted', 'arrow keys move and select within the radio group (got '+picked+')');

ck(await p.locator('#h1 .cur').first().evaluate(e=>e.open), 'recording a verdict opens the curator finding');
ck(await p.locator('#h1').first().evaluate(e=>e.dataset.answered==='1'), 'claim marked answered');
ck((await p.textContent('#done'))==='1', 'tally incremented to 1');
const agree = await p.textContent('#h1 .agree-note');
ck(/matches the curator/.test(agree), 'agreement reported: "'+agree.trim()+'"');
ck((await p.textContent('#status')).includes('agree on 1 of 1'), 'status line reports agreement');
ck((await p.textContent('#sheet-body')).includes('Bob Hope'), 'finding sheet built');

/* the citation step: hidden until a verdict exists, then usable */
ck(!(await p.locator('#h2 .cite').first().isVisible()), 'citation step hidden before a verdict is recorded');
ck(await p.locator('#h1 .cite').first().isVisible(), 'citation step appears once a verdict is recorded');
await p.locator('#h1 .cite input[value="2"]').check();
ck((await p.textContent('#sheet-body')).includes('Settled on evidence 2'), 'citation recorded on the finding sheet');
await p.locator('#h1 .cite input[value="0"]').check();
ck((await p.textContent('#sheet-body')).includes('none of the evidence convinced me'),
   'visitor may reject the curator\u2019s own evidence');

/* a disagreement must be recorded, not corrected */
await p.locator('#m1 input[value=confirmed]').check();
const dis = await p.textContent('#m1 .agree-note');
ck(/curator said Contradicted/i.test(dis), 'disagreement recorded without overriding the visitor');
ck(await p.locator('#m1 .cur').first().evaluate(e=>e.open), 'curator reasoning shown even when you disagree');

/* clear */
await p.click('#clear-sheet');
ck((await p.textContent('#done'))==='0', 'clear resets the tally');
ck((await p.locator('.cur[open]').count())===0, 'clear re-closes the curator findings');
ck((await p.textContent('#sheet-body')).includes('No findings recorded'), 'clear empties the sheet');
ck(errs.length===0, 'no JS errors ('+(errs[0]||'none')+')');


/* EVERY case file, not just the first — the citation listener used to be bound to
   the first .claims list's parent section, so case files 2-5 silently dropped
   their citations. A happy-path test on case file 1 passed anyway. */
await p.click('#clear-sheet');
const CASES=[['h1','Bob Hope'],['e1','Albert Einstein'],['m1','John Muir'],['a1','Madeleine Albright'],['c1','Celia Cruz']];
let allCited=true, allVerdicts=true;
for (const [id,name] of CASES){
  await p.locator('#'+id+' .vd input').first().check();
  await p.locator('#'+id+' .cite input[value="0"]').check();
  await p.waitForTimeout(80);
  const txt=await p.textContent('#sheet-body');
  if(!txt.includes(name)) allVerdicts=false;
}
const cited=((await p.textContent('#sheet-body')).match(/none of the evidence/g)||[]).length;
ck(allVerdicts, 'verdicts register in all 5 case files');
ck(cited===5, 'citations register in all 5 case files (got '+cited+' of 5)');
ck((await p.textContent('#done'))==='5', 'tally counts across case files');
await p.click('#clear-sheet');

/* Enter in the search field must filter, not reload and wipe */
const ctx2=await b.newContext({viewport:{width:1280,height:900}});
const p2=await ctx2.newPage();
await p2.goto('http://127.0.0.1:8731/inductees.html',{waitUntil:'load'});
await p2.locator('#q').fill('Vienna'); await p2.waitForTimeout(100);
const beforeEnter=(await p2.textContent('#count')).trim();
await p2.locator('#q').press('Enter'); await p2.waitForTimeout(300);
const afterEnter=(await p2.textContent('#count')).trim();
ck(beforeEnter===afterEnter, 'Enter in the search field keeps the filter ("'+beforeEnter+'" -> "'+afterEnter+'")');
ck(!p2.url().includes('?'), 'Enter does not reload the page');
await ctx2.close();

/* The exhibit modal: Space belongs to the focused button; Tab stays trapped */
const ctx3=await b.newContext({viewport:{width:1280,height:900}});
const p3=await ctx3.newPage();
await p3.goto('http://127.0.0.1:8731/albright.html',{waitUntil:'load'});
await p3.getByRole('button',{name:'Exhibit mode',exact:true}).click(); await p3.waitForTimeout(250);
await p3.getByRole('button',{name:'Close (Esc)',exact:true}).focus();
await p3.keyboard.press('Space'); await p3.waitForTimeout(250);
ck(!(await p3.evaluate(()=>document.querySelector('.ihh-stage').classList.contains('on'))),
   'Space on the Close button closes the modal');
await p3.getByRole('button',{name:'Exhibit mode',exact:true}).click(); await p3.waitForTimeout(250);
await p3.keyboard.press('Shift+Tab'); await p3.waitForTimeout(150);
ck(await p3.evaluate(()=>!!document.activeElement.closest('.ihh-stage')),
   'Shift+Tab from the opening focus stays inside the modal');
await p3.keyboard.press('Escape');
await ctx3.close();

/* axe again with every drawer forced open — the state axe cannot see by default */
await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
await p.addScriptTag({path:'node_modules/axe-core/axe.min.js'});
const r=await p.evaluate(async()=>{
  const x=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
  return x.violations.map(v=>v.id+'×'+v.nodes.length);
});
ck(r.length===0, 'axe clean with ALL drawers open '+(r.length?JSON.stringify(r):''));

/* target size (WCAG 2.2 SC 2.5.8 — 24×24 minimum) */
const small = await p.evaluate(()=>{
  const bad=[];
  document.querySelectorAll('a,button,summary,label.vd-opts>*,.vd-opts label,input').forEach(e=>{
    const r=e.getBoundingClientRect();
    if(r.width&&r.height&&(r.width<24||r.height<24)) bad.push(e.tagName+'.'+(e.className||'')+' '+Math.round(r.width)+'x'+Math.round(r.height));
  });
  return bad;
});
ck(small.length===0, 'all targets ≥24×24 '+(small.length?JSON.stringify(small.slice(0,4)):''));
await ctx.close();

/* ── 2. with JavaScript DISABLED ────────────────────────────────── */
ctx=await b.newContext({javaScriptEnabled:false,viewport:{width:1280,height:900}});
p=await ctx.newPage();
await p.goto(U,{waitUntil:'load'});
const nC = await p.locator('.cl').count();
const nE = await p.locator('.ev-list li').count();
ck(nC === N.claims, 'no-JS: all '+N.claims+' claims present');
ck(nE === N.evidence, 'no-JS: all '+N.evidence+' evidence items present');
ck(await p.locator('.stamp').count()===nC, "no-JS: every curator verdict still in the page");
ck(await p.locator('.lesson').count()===nC, 'no-JS: every lesson still readable');
const nV = await p.locator('.vd input[type=radio]').count();
const nS = await p.locator('.cite input[type=radio]').count();
ck(nV === N.claims*3, 'no-JS: '+nV+' verdict controls (3 per claim) still usable');
ck(nS === N.evidence + N.claims, 'no-JS: '+nS+' citation controls (one per evidence item plus "none") still usable');
ck(await p.locator('#h1 .cite').first().isVisible(), 'no-JS: the citation step is visible (not gated on script)');
await p.locator('#h1 .ev').first().evaluate(e=>e.open=true);
ck(await p.locator('#h1 .ev-list li').first().isVisible(), 'no-JS: evidence drawer opens natively');
await ctx.close();
await b.close();

console.log('\nPASS ('+pass.length+')'); pass.forEach(m=>console.log('  ✓ '+m));
if(fail.length){console.log('\nFAIL ('+fail.length+')'); fail.forEach(m=>console.log('  ✗ '+m)); process.exit(1);}
console.log('\nALL '+pass.length+' CHECKS PASSED');
