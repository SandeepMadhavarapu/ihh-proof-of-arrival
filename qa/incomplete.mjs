import { PAGES } from './catalog.mjs';
import { chromium } from 'playwright';

const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
let inc=0, reasons={};
for (const pg of PAGES){
  const ctx=await b.newContext({viewport:{width:1280,height:900}});
  const p=await ctx.newPage();
  await p.goto('http://127.0.0.1:8731/'+pg+'.html',{waitUntil:'load'});
  await p.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=true));
  await p.addScriptTag({path:'node_modules/axe-core/axe.min.js'});
  const r=await p.evaluate(async()=>{
    const x=await axe.run(document,{runOnly:['color-contrast']});
    return x.incomplete.flatMap(v=>v.nodes.map(n=>
      (n.any&&n.any[0]&&n.any[0].message||'unstated').replace(/\s+/g,' ').slice(0,90)));});
  inc+=r.length; r.forEach(m=>reasons[m]=(reasons[m]||0)+1);
  await ctx.close();
}
console.log('axe "incomplete" colour-contrast nodes across 11 pages: '+inc);
Object.entries(reasons).sort((a,b)=>b[1]-a[1]).forEach(([m,n])=>console.log('  '+n+'×  '+m));
await b.close();
