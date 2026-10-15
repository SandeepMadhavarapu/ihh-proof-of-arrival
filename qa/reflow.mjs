import { chromium } from 'playwright';
const PAGES=['index','inductees','verify','method','albright','lamarr','pei','cruz','share','about','rights','accessibility','privacy','404'];
const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
let bad=0;
/* SC 1.4.10 Reflow: no two-dimensional scrolling at 320 CSS px wide.
   SC 1.4.4 Resize Text: usable at 200%. 1280/2 = 640 emulates 200% zoom. */
for (const [label,w] of [['320px (reflow)',320],['640px (=200% zoom)',640]]){
  let n=0;
  for (const pg of PAGES){
    const ctx=await b.newContext({viewport:{width:w,height:900}});
    const p=await ctx.newPage();
    await p.goto('http://127.0.0.1:8731/'+pg+'.html',{waitUntil:'load'});
    await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
    await p.waitForTimeout(120);
    const r=await p.evaluate(()=>{
      const de=document.documentElement;
      const over=[];
      document.querySelectorAll('*').forEach(e=>{
        const b=e.getBoundingClientRect();
        if(b.width>0 && b.right > de.clientWidth+1)
          over.push(e.tagName+'.'+(typeof e.className==='string'?e.className.split(' ')[0]:'')+' r='+Math.round(b.right));
      });
      return {scrollW:de.scrollWidth, clientW:de.clientWidth, over:over.slice(0,3)};
    });
    const horiz = r.scrollW > r.clientW + 1;
    if (horiz){bad++;n++; console.log('  ✗',label,pg,'scrollWidth',r.scrollW,'>',r.clientW, JSON.stringify(r.over));}
    await ctx.close();
  }
  console.log((n?'':'  ✓ ')+label+': '+(n?'FAILURES ABOVE':'all '+PAGES.length+' pages reflow with no horizontal scrolling'));
}
await b.close();
process.exit(bad?1:0);
