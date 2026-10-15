import { chromium } from 'playwright';
const PAGES=['index','inductees','verify','method','albright','lamarr','pei','cruz','share','about','rights','accessibility','privacy','404'];
const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
let bad=0;

/* Everything a visitor must be able to see and reach with no script running,
   at BOTH widths — the audit found the nav was unreachable only on a phone. */
for (const [label,w,h] of [['phone 375',375,812],['desktop 1280',1280,900]]){
  for (const pg of PAGES){
    const ctx=await b.newContext({javaScriptEnabled:false,viewport:{width:w,height:h}});
    const p=await ctx.newPage();
    await p.goto('http://127.0.0.1:8731/'+pg+'.html',{waitUntil:'load'});
    const r=await p.evaluate(()=>{
      const faults=[];
      /* 1. no text content may be invisible */
      document.querySelectorAll('p,li,h1,h2,h3,h4,dd,blockquote,figcaption').forEach(e=>{
        if(!e.textContent.trim()) return;
        const cs=getComputedStyle(e);
        if(parseFloat(cs.opacity)===0 || cs.visibility==='hidden' || cs.display==='none'){
          /* a closed <details> legitimately hides its own content */
          if(e.closest('details:not([open])')) return;
          if(e.closest('[hidden]')) return;
        /* explicitly declared as describing a script-only feature */
        if(e.closest('[data-js-only]')) return;
          faults.push('invisible '+e.tagName+': "'+e.textContent.trim().slice(0,40)+'" ('+cs.opacity+'/'+cs.visibility+'/'+cs.display+')');
        }});
      /* 2. the navigation must be reachable */
      const nav=document.querySelector('#nav');
      if(nav && getComputedStyle(nav).display==='none')
        faults.push('navigation is display:none and the menu button needs a script');
      /* 3. every nav link must be reachable */
      const links=[...document.querySelectorAll('#nav a')].filter(a=>a.offsetParent!==null||getComputedStyle(a).display!=='none');
      if(nav && links.length===0) faults.push('no reachable navigation links');
      return faults;
    });
    if(r.length){bad+=r.length; console.log('  ✗ '+label+' '+pg+':'); r.forEach(x=>console.log('      '+x));}
    await ctx.close();
  }
  console.log('  '+(bad?'':'✓ ')+label+', no JavaScript: '+(bad?'see above':'all '+PAGES.length+' pages fully readable and navigable'));
}
await b.close();
console.log(bad? '\nNO-JS FAULTS: '+bad : '\nNo content is hidden behind JavaScript on any page, at either width.');
process.exit(bad?1:0);
