import { chromium } from 'playwright';
const U=process.env.PROFILE_URL;
if(!U){ console.error('PROFILE_URL is required'); process.exit(2); }
const b=await chromium.launch({executablePath:process.env.CHROMIUM||'/usr/bin/chromium',args:['--no-sandbox']});
const pass=[],fail=[]; const ck=(c,m)=>(c?pass:fail).push(m);
for(const scheme of ['light','dark']){
  const ctx=await b.newContext({viewport:{width:1280,height:900},colorScheme:scheme});
  const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(String(e)));
  await p.goto(U,{waitUntil:'load'}); await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  await p.addScriptTag({path:'node_modules/axe-core/axe.min.js'});
  const v=await p.evaluate(async()=>{const r=await axe.run(document.querySelector('.ihh-profile'),{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});return r.violations.map(x=>x.id+'×'+x.nodes.length)});
  ck(v.length===0,scheme+': generated profile axe clean '+(v.length?JSON.stringify(v):''));
  ck(errs.length===0,scheme+': generated profile has no page errors');
  await ctx.close();
}
for(const w of [320,360,390,430,768,1280]){
  const ctx=await b.newContext({viewport:{width:w,height:900}}); const p=await ctx.newPage();
  await p.goto(U,{waitUntil:'load'}); await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  const over=await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1);
  ck(!over,'generated profile: no horizontal scroll at '+w+'px'); await ctx.close();
}
const ctx=await b.newContext({viewport:{width:1280,height:900},javaScriptEnabled:false}); const p=await ctx.newPage(); await p.goto(U,{waitUntil:'load'});
const a=await p.evaluate(()=>({scripts:document.querySelectorAll('.ihh-profile script').length,external:[...document.querySelectorAll('.ihh-profile [src]')].map(e=>e.getAttribute('src')).filter(x=>/^(https?:)?\/\//.test(x||'')).length,status:document.querySelector('.ihh-profile .status')?.textContent||'',sections:document.querySelectorAll('.ihh-profile details.sec').length}));
ck(a.scripts===0,'generated profile has zero scripts'); ck(a.external===0,'generated profile loads zero external resources'); ck(/REQUIRES HUMAN SIGN-OFF/.test(a.status),'generated profile exposes human sign-off status'); ck(a.sections===5,'generated profile has five narrative sections'); await ctx.close(); await b.close();
pass.forEach(x=>console.log('  ✓ '+x)); if(fail.length){fail.forEach(x=>console.log('  ✗ '+x));process.exit(1)} console.log('\nALL '+pass.length+' PROFILE FACTORY CHECKS PASSED');
