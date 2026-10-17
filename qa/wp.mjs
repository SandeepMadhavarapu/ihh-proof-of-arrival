import { IND, ORIGINAL, expected } from './catalog.mjs';
import { chromium } from 'playwright';

const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const pass=[],fail=[]; let who=''; const ck=(c,m)=>(c?pass:fail).push(who+': '+m);
for (const n of IND){ who=n; const U='http://127.0.0.1:8741/inductees/'+n+'/preview.html';

for (const scheme of ['light','dark']){
  const ctx=await b.newContext({viewport:{width:1280,height:900},colorScheme:scheme});
  const p=await ctx.newPage();
  const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto(U,{waitUntil:'load'});
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  await p.addScriptTag({path:'node_modules/axe-core/axe.min.js'});
  const r=await p.evaluate(async()=>{
    const x=await axe.run(document.querySelector('.ihh-profile'),
      {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
    return x.violations.map(v=>v.id+'×'+v.nodes.length+' :: '+(v.nodes[0]?.failureSummary||'').replace(/\n/g,' ').slice(0,110));});
  ck(r.length===0, scheme+': axe clean on the fragment '+(r.length?JSON.stringify(r):''));
  ck(errs.length===0, scheme+': no JS errors');
  await ctx.close();
}

const ctx=await b.newContext({viewport:{width:1280,height:900}});
const p=await ctx.newPage(); await p.goto(U,{waitUntil:'load'});

/* anatomy checks, measured not asserted */
const a=await p.evaluate(()=>{
  const prof=document.querySelector('.ihh-profile');
  const open=prof.querySelector('.opening'), fig=prof.querySelector('figure.anchor'),
        cap=fig.querySelector('figcaption'), sf=prof.querySelector('.standfirst');
  const r=e=>e.getBoundingClientRect();
  const media=fig.querySelector('img,.ph');
  // is any text painted ON TOP of the media box?
  /* "No text overlaid on the photograph" is the headline requirement of the page spec,
     so this check must be capable of failing. An earlier version carried a dangling
     ternary that excluded every statically positioned element — i.e. all normal-flow
     text — which made the check unfalsifiable. Any box that intersects the media box
     now counts, whatever its position value. */
  const mb=r(media);
  const overlay=[...prof.querySelectorAll('p,h1,h2,h3,h4,blockquote,span,figcaption,cite,li')]
    .filter(e=>e.textContent.trim() && !media.contains(e) && e!==media)
    .filter(e=>!e.closest('.ph'))
    .filter(e=>{
      const b=r(e);
      return b.width>0 && b.height>0 &&
             b.top < mb.bottom-2 && b.bottom > mb.top+2 &&
             b.left < mb.right-2 && b.right > mb.left+2;})
    .map(e=>e.tagName+':'+e.textContent.trim().slice(0,24));
  return {
    openingAboveMedia: r(open).bottom <= mb.top + 1,
    captionBelowMedia: r(cap).top >= mb.bottom - 1,
    standfirstExists: !!sf,
    overlay,
    scripts: prof.querySelectorAll('script').length,
    // links to sources are REQUIRED; what must be absent is external *resources*
    externalRefs: [...prof.querySelectorAll('[src], link[href], iframe, object, embed')]
      .map(e=>e.getAttribute('src')||e.getAttribute('href')||'')
      .filter(u=>/^(https?:)?\/\//.test(u)).length,
    sourceLinks: prof.querySelectorAll('a[href^="https://"], a[href^="http://"]').length,
    sections: prof.querySelectorAll('details.sec').length,
    sourceItems: prof.querySelectorAll('.src-item').length,
    questions: prof.querySelectorAll('ol.qs li').length,
    activities: prof.querySelectorAll('ol.acts li').length,
    quotes: prof.querySelectorAll('blockquote.pull').length,
    h1: prof.querySelectorAll('h1').length,
    fillme: prof.querySelectorAll('.fillme').length,
  };});
ck(a.openingAboveMedia, 'opening sentence sits ABOVE the photograph');
ck(a.captionBelowMedia, 'credit sits immediately BENEATH the photograph');
ck(a.overlay.length===0, 'no text overlaid on the photograph '+(a.overlay.length?JSON.stringify(a.overlay.slice(0,3)):''));
ck(a.standfirstExists, 'standfirst present');
ck(a.sections===5, 'exactly 5 sections (got '+a.sections+')');
if (ORIGINAL.includes(n)) ck(a.sourceItems>=10&&a.sourceItems<=15, a.sourceItems+' source items (original 10-15 contract)');
ck(a.sourceItems>0, 'source register is nonempty');
ck(a.questions===5, 'exactly 5 discussion questions (got '+a.questions+')');
ck(a.activities===2, 'exactly 2 activities (got '+a.activities+')');
ck(a.quotes===expected(n).quotes, 'quotation count matches authored optional quotation (got '+a.quotes+')');
ck(a.h1===1, 'exactly one h1');
ck(a.scripts===0, 'ZERO script elements in the fragment');
ck(a.externalRefs===0, 'zero external RESOURCES loaded (got '+a.externalRefs+')');
ck(a.sourceLinks>=a.sourceItems, a.sourceLinks+' evidence links cover the source register');
if (ORIGINAL.includes(n)) ck(a.sourceLinks>=10, 'original profile retains 10+ evidence links');
ck(a.fillme===2, 'byline placeholders are visibly marked for the volunteer (got '+a.fillme+')');

/* scoping: the hostile theme must not reach in, and the fragment must not reach out */
const scope=await p.evaluate(()=>{
  const inside=getComputedStyle(document.querySelector('.ihh-profile h2'));
  const outside=getComputedStyle(document.querySelector('.host-chrome'));
  return {insideFont:inside.fontFamily.split(',')[0], insideTransform:inside.textTransform,
          insideAlign:inside.textAlign, outsideFont:outside.fontFamily.split(',')[0]};});
ck(!/Impact/i.test(scope.insideFont), "theme's Impact heading font does not reach inside (got "+scope.insideFont+")");
ck(scope.insideTransform==='none', "theme's uppercase transform does not reach inside");
ck(/Verdana/i.test(scope.outsideFont), "fragment's styles do not leak out to the host");

/* keyboard: every section reachable and operable with no mouse */
await p.keyboard.press('Tab');
let reached=0;
for(let i=0;i<40;i++){
  const t=await p.evaluate(()=>document.activeElement.tagName+'|'+(document.activeElement.className||''));
  if(t.startsWith('SUMMARY')) reached++;
  await p.keyboard.press('Tab');
}
ck(reached>=5, 'all 5 section headers reachable by Tab (reached '+reached+')');
const first=p.locator('.ihh-profile details.sec').first();
await first.locator('summary').focus();
await p.keyboard.press('Enter');
ck(!(await first.evaluate(e=>e.open)), 'Enter toggles a section closed');
await p.keyboard.press('Enter');
ck(await first.evaluate(e=>e.open), 'Enter toggles it open again');

/* reflow at every required width */
for (const w of [320,360,390,430,768,1280]){
  await p.setViewportSize({width:w,height:900});
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  await p.waitForTimeout(100);
  const over=await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);
  ck(!over, 'no horizontal scrolling at '+w+'px');
}
await ctx.close();
}
await b.close();
pass.forEach(m=>console.log('  ✓ '+m));
if(fail.length){console.log(''); fail.forEach(m=>console.log('  ✗ '+m)); console.log('\n'+fail.length+' FAILED of '+(pass.length+fail.length)); process.exit(1);}
console.log('\nALL '+pass.length+' CHECKS PASSED');
