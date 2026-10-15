import { chromium } from 'playwright';
const PAGES=['index','inductees','verify','method','albright','lamarr','pei','cruz','share','about','rights','accessibility','privacy','404'];
const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
let total=0;
for (const scheme of ['light','dark']){
  let n=0;
  for (const pg of PAGES){
    const ctx=await b.newContext({colorScheme:scheme,viewport:{width:1280,height:900}});
    const p=await ctx.newPage();
    await p.goto('http://127.0.0.1:8731/'+pg+'.html',{waitUntil:'load'});
    /* press every toggle button, open every disclosure — audit found the dark
       failure only existed in a pressed state */
    await p.evaluate(()=>{document.querySelectorAll('details').forEach(d=>d.open=true);
      document.querySelectorAll('button[aria-pressed]').forEach(x=>x.click());});
    await p.waitForTimeout(200);
    await p.addScriptTag({path:'node_modules/axe-core/axe.min.js'});
    const r=await p.evaluate(async()=>{
      const x=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
      return {v:x.violations.map(v=>({id:v.id,n:v.nodes.length,
               why:(v.nodes[0]&&v.nodes[0].failureSummary||'').replace(/\n/g,' ').slice(0,150)})),
              inc:x.incomplete.reduce((a,i)=>a+i.nodes.length,0)};});
    if(r.v.length){n+=r.v.reduce((a,x)=>a+x.n,0); console.log('  ✗',scheme,pg,JSON.stringify(r.v));}
    total+=r.v.reduce((a,x)=>a+x.n,0);
    await ctx.close();
  }
  console.log((n?'  ':'  ✓ ')+scheme+' scheme, toggles pressed, disclosures open: '+(n?n+' violations':'0 violations across '+PAGES.length+' pages'));
}
console.log('\nTOTAL: '+total);
await b.close(); process.exit(total?1:0);
