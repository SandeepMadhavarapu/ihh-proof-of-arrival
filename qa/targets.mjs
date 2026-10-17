import { PAGES } from './catalog.mjs';
import { chromium } from 'playwright';

const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
let bad=0;
for (const pg of PAGES){
  const ctx=await b.newContext({viewport:{width:1280,height:900}});
  const p=await ctx.newPage();
  await p.goto('http://127.0.0.1:8731/'+pg+'.html',{waitUntil:'load'});
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  const out=await p.evaluate(()=>{
    const res=[];
    document.querySelectorAll('a[href],button,summary,input,select,textarea').forEach(e=>{
      const r=e.getBoundingClientRect();
      if(!r.width||!r.height) return;
      if(r.width>=24&&r.height>=24) return;
      // SC 2.5.8 "Inline" exception: a link sitting inside a run of text
      const par=e.closest('p,li,blockquote,td,h1,h2,h3,h4,figcaption,summary,label');
      const inlineRun = e.tagName==='A' && par &&
        par.textContent.trim().length > e.textContent.trim().length + 8;
      if(inlineRun) return;
      res.push({t:e.tagName,c:e.className||'',txt:(e.textContent||'').trim().slice(0,38),
                w:Math.round(r.width),h:Math.round(r.height)});
    });
    return res;
  });
  if(out.length){bad+=out.length; console.log(pg+':'); out.forEach(o=>console.log('   ',o.t,'"'+o.txt+'"',o.c,o.w+'x'+o.h));}
  await ctx.close();
}
console.log(bad? '\nUNDERSIZED NON-INLINE TARGETS: '+bad : '\nEvery non-inline target on all '+PAGES.length+' pages is at least 24x24.');
await b.close();
process.exit(bad?1:0);
