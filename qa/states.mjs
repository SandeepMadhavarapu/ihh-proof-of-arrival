import { chromium } from 'playwright';
const SITE='http://127.0.0.1:8731/', WP='http://127.0.0.1:8741/inductees/albright/preview.html';
const PAGES=['index','inductees','verify','method','albright','lamarr','pei','cruz','share','about','rights','accessibility','privacy','404'];
const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const pass=[],fail=[]; const ck=(c,m)=>(c?pass:fail).push(m);

/* reduced motion: nothing may animate or transition */
{
  const ctx=await b.newContext({viewport:{width:1280,height:900},reducedMotion:'reduce'});
  const p=await ctx.newPage();
  let moving=[];
  for (const pg of PAGES){
    await p.goto(SITE+pg+'.html',{waitUntil:'load'}); await p.waitForTimeout(150);
    const m=await p.evaluate(()=>{
      const bad=[];
      document.querySelectorAll('*').forEach(e=>{
        const cs=getComputedStyle(e);
        const t=parseFloat(cs.transitionDuration)||0, a=parseFloat(cs.animationDuration)||0;
        if(t>0||a>0) bad.push(e.tagName+'.'+(typeof e.className==='string'?e.className.split(' ')[0]:'')
          +' t='+cs.transitionDuration+' a='+cs.animationDuration);
      });
      return bad.slice(0,3);});
    if(m.length) moving.push(pg+': '+JSON.stringify(m));
  }
  ck(moving.length===0, 'prefers-reduced-motion: nothing animates on any page '+(moving.length?JSON.stringify(moving.slice(0,2)):''));
  await ctx.close();
}

/* print: collapsed content must open, chrome must go */
{
  const ctx=await b.newContext({viewport:{width:1100,height:1400}});
  const p=await ctx.newPage();
  await p.goto(SITE+'albright.html',{waitUntil:'load'});
  await p.emulateMedia({media:'print'}); await p.waitForTimeout(250);
  const r=await p.evaluate(()=>{
    const hiddenDetail=[...document.querySelectorAll('details:not([open]) > *:not(summary)')]
      .filter(e=>getComputedStyle(e).display==='none').length;
    const chrome=[...document.querySelectorAll('.site-head,.site-foot,.ihh .bar,.ihh-stage')]
      .filter(e=>getComputedStyle(e).display!=='none').length;
    return {hiddenDetail, chrome};});
  ck(r.hiddenDetail===0, 'print: every collapsed section opens ('+r.hiddenDetail+' still hidden)');
  ck(r.chrome===0, 'print: interface chrome is removed ('+r.chrome+' still shown)');
  await p.goto(WP,{waitUntil:'load'}); await p.emulateMedia({media:'print'}); await p.waitForTimeout(200);
  const w=await p.evaluate(()=>[...document.querySelectorAll('.ihh-profile details:not([open]) > *:not(summary)')]
      .filter(e=>getComputedStyle(e).display==='none').length);
  ck(w===0, 'print: WordPress fragment opens all sections ('+w+' hidden)');
  await ctx.close();
}

/* every required width, both deliverables, disclosures open */
for (const w of [320,360,390,430,768,1280,1600]){
  const ctx=await b.newContext({viewport:{width:w,height:900}});
  const p=await ctx.newPage();
  let over=[];
  for (const pg of PAGES){
    await p.goto(SITE+pg+'.html',{waitUntil:'load'});
    await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
    await p.waitForTimeout(90);
    if(await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1)) over.push(pg);
  }
  await p.goto(WP,{waitUntil:'load'});
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  await p.waitForTimeout(90);
  if(await p.evaluate(()=>document.documentElement.scrollWidth>document.documentElement.clientWidth+1)) over.push('inductees/albright');
  ck(over.length===0, w+'px: no horizontal scrolling on '+PAGES.length+' pages + the WP fragment '+(over.length?JSON.stringify(over):''));
  await ctx.close();
}

/* focus visibility and return, keyboard only, on the interactive page */
{
  const ctx=await b.newContext({viewport:{width:1280,height:900}});
  const p=await ctx.newPage();
  await p.goto(SITE+'verify.html',{waitUntil:'load'});
  let invisible=0, n=0;
  for(let i=0;i<30;i++){
    await p.keyboard.press('Tab');
    const ok=await p.evaluate(()=>{
      const e=document.activeElement; if(!e||e===document.body) return true;
      const cs=getComputedStyle(e);
      const transparent=c=>/rgba\([^)]*,\s*0\s*\)/.test(c||'');
      const ol=parseFloat(cs.outlineWidth)||0;
      const olVisible = ol>0 && cs.outlineStyle!=='none' && !transparent(cs.outlineColor);
      const sh=cs.boxShadow||'';
      const shVisible = sh!=='none' && sh!=='' && !transparent(sh) &&
        (sh.match(/-?\d+(?:\.\d+)?px/g)||[]).some(v=>Math.abs(parseFloat(v))>0);
      return olVisible||shVisible;});
    n++; if(!ok) invisible++;
  }
  ck(invisible===0, 'keyboard: every one of '+n+' focus stops shows a visible indicator ('+invisible+' did not)');
  await ctx.close();
}
await b.close();
pass.forEach(m=>console.log('  ✓ '+m));
if(fail.length){console.log(''); fail.forEach(m=>console.log('  ✗ '+m)); console.log('\n'+fail.length+' FAILED'); process.exit(1);}
console.log('\nALL '+pass.length+' STATE CHECKS PASSED');
