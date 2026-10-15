import fs from 'node:fs';
import { chromium } from 'playwright';
const U=process.env.PROFILE_URL;
if(!U){ console.error('PROFILE_URL is required'); process.exit(2); }
fs.mkdirSync('qa-out/profile-factory',{recursive:true});
const b=await chromium.launch({executablePath:process.env.CHROMIUM||'/usr/bin/chromium',args:['--no-sandbox']});
const pass=[],fail=[]; const ck=(c,m)=>(c?pass:fail).push(m);

for(const scheme of ['light','dark']){
  const ctx=await b.newContext({viewport:{width:1280,height:900},colorScheme:scheme});
  const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto(U,{waitUntil:'load'}); await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  await p.screenshot({path:`qa-out/profile-factory/desktop-${scheme}.png`,fullPage:true});
  await p.addScriptTag({path:'node_modules/axe-core/axe.min.js'});
  const axeResult=await p.evaluate(async()=>{const r=await axe.run(document.querySelector('.ihh-profile'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});return {v:r.violations.map(x=>x.id+'×'+x.nodes.length),incomplete:r.incomplete.map(x=>x.id+'×'+x.nodes.length)}});
  ck(axeResult.v.length===0,scheme+': generated profile axe clean '+(axeResult.v.length?JSON.stringify(axeResult.v):''));
  ck(errs.length===0,scheme+': generated profile has no page errors');
  const semantics=await p.evaluate(()=>{
    const undersized=[];
    document.querySelectorAll('.ihh-profile a[href],.ihh-profile summary').forEach(e=>{
      const r=e.getBoundingClientRect();
      if(!r.width||!r.height|| (r.width>=24&&r.height>=24)) return;
      // WCAG 2.5.8 inline exception: a text link inside a larger run of prose may be smaller.
      const par=e.closest('p,li,blockquote,figcaption,summary,label');
      const inlineRun=e.tagName==='A' && par && par.textContent.trim().length > e.textContent.trim().length + 8;
      if(!inlineRun) undersized.push({tag:e.tagName,text:(e.textContent||'').trim().slice(0,40),w:Math.round(r.width),h:Math.round(r.height)});
    });
    return {h1:document.querySelectorAll('.ihh-profile h1').length,main:document.querySelectorAll('.ihh-profile main').length,status:document.querySelector('.ihh-profile .status')?.textContent||'',sourceDeck:!!document.querySelector('.ihh-profile .source-deck'),undersized};
  });
  ck(semantics.h1===1,scheme+': exactly one profile h1');
  ck(semantics.main===1,scheme+': exactly one profile main landmark');
  ck(semantics.sourceDeck,scheme+': provenance register is present');
  ck(semantics.undersized.length===0,scheme+': every non-inline summary/link meets 24px target floor '+(semantics.undersized.length?JSON.stringify(semantics.undersized):''));
  await ctx.close();
}

for(const w of [320,360,375,390,412,430,640,768,1024,1280,1440]){
  const ctx=await b.newContext({viewport:{width:w,height:900}}); const p=await ctx.newPage();
  await p.goto(U,{waitUntil:'load'}); await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  if(w===390) await p.screenshot({path:'qa-out/profile-factory/mobile-390-light.png',fullPage:true});
  const dims=await p.evaluate(()=>({over:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,body:document.body.getBoundingClientRect().width,doc:document.documentElement.clientWidth}));
  ck(!dims.over,'generated profile: no horizontal scroll at '+w+'px');
  await ctx.close();
}

{
  const ctx=await b.newContext({viewport:{width:390,height:900},javaScriptEnabled:false}); const p=await ctx.newPage(); await p.goto(U,{waitUntil:'load'});
  const a=await p.evaluate(()=>({
    scripts:document.querySelectorAll('.ihh-profile script').length,
    externalSrc:[...document.querySelectorAll('.ihh-profile [src]')].map(e=>e.getAttribute('src')).filter(x=>/^(https?:)?\/\//.test(x||'')).length,
    runtime:document.querySelectorAll('.ihh-profile link,.ihh-profile iframe,.ihh-profile object,.ihh-profile embed').length,
    unsafeHref:[...document.querySelectorAll('.ihh-profile a[href]')].filter(a=>/^(javascript|data|file|vbscript):/i.test((a.getAttribute('href')||'').trim())).length,
    status:document.querySelector('.ihh-profile .status')?.textContent||'',
    sections:document.querySelectorAll('.ihh-profile details.sec').length,
    text:(document.querySelector('.ihh-profile')?.innerText||'').length,
  }));
  ck(a.scripts===0,'generated profile has zero scripts');
  ck(a.externalSrc===0,'generated profile loads zero external src resources');
  ck(a.runtime===0,'generated profile has zero link/iframe/object/embed runtime dependencies');
  ck(a.unsafeHref===0,'generated profile has zero unsafe href schemes');
  ck(/REQUIRES HUMAN SIGN-OFF/.test(a.status),'generated profile exposes human sign-off status');
  ck(a.sections===5,'generated profile has five narrative sections');
  ck(a.text>500,'generated profile remains substantive with JavaScript disabled');
  await ctx.close();
}

{
  const ctx=await b.newContext({viewport:{width:390,height:900},reducedMotion:'reduce'}); const p=await ctx.newPage(); await p.goto(U,{waitUntil:'load'});
  const motion=await p.evaluate(()=>[...document.querySelectorAll('.ihh-profile *')].every(e=>{const s=getComputedStyle(e);return parseFloat(s.animationDuration||'0')===0&&parseFloat(s.transitionDuration||'0')===0}));
  ck(motion,'generated profile honors reduced motion with no active animation/transition');
  await ctx.close();
}

{
  const ctx=await b.newContext({viewport:{width:800,height:1000}}); const p=await ctx.newPage(); await p.goto(U,{waitUntil:'load'}); await p.emulateMedia({media:'print'}); await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  const printOver=await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);
  ck(!printOver,'generated profile print layout has no horizontal overflow');
  await ctx.close();
}

await b.close();
pass.forEach(x=>console.log('  ✓ '+x));
if(fail.length){fail.forEach(x=>console.log('  ✗ '+x));process.exit(1)}
console.log('\nALL '+pass.length+' PROFILE FACTORY CHECKS PASSED');
