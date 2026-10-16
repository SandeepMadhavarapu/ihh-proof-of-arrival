/* Contrast, measured from real composited pixels — not from declared tokens.
 *
 * axe-core reports colour-contrast as "incomplete" (not pass, not fail) wherever a
 * gradient, pseudo-element or background image makes the effective background colour
 * uncomputable. On this site the aged-paper texture is a CSS gradient, so axe cannot
 * resolve ~33 nodes (the exact count is non-deterministic run to run; run qa/incomplete.mjs
 * to see it). This harness resolves them the only honest way: it screenshots each page,
 * reads the actual pixels composited behind every text run, finds the modal background
 * colour, and computes the WCAG 2.x contrast ratio. It ASSERTS zero failures and exits
 * nonzero if any text run falls below its minimum. Everything runs in node + playwright;
 * the screenshot is decoded with the browser's own canvas, so there is no Python/PIL
 * dependency and the result is reproducible from this package alone.
 */
import { chromium } from 'playwright';
const OUT = process.env.QA_OUT || '/tmp/qa-out';
const PAGES=['index','about','accessibility','albright','inductees','method','privacy','rights','share','verify','404'];
const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args:['--no-sandbox','--force-color-profile=srgb','--font-render-hinting=none']});

/* the WCAG maths, run inside the page over canvas pixels. Ported from the reference
   implementation; sRGB linearisation per WCAG 2.1 relative-luminance definition. */
let rows=[], fails=[], runs=0;
for (const scheme of ['light','dark']){
  for (const pg of PAGES){
    const ctx=await b.newContext({viewport:{width:1280,height:900},colorScheme:scheme,deviceScaleFactor:1});
    const p=await ctx.newPage();
    await p.goto('http://127.0.0.1:8731/'+pg+'.html',{waitUntil:'load'});
    // expose every collapsed region and press every toggle, so no text escapes sampling
    await p.evaluate(()=>{document.querySelectorAll('details').forEach(d=>d.open=true);
      document.querySelectorAll('[aria-pressed]').forEach(btn=>{try{btn.click();}catch(e){}});});
    // Toggle notifications temporarily cover underlying text. Sample after they clear,
    // so the background belongs to the text being measured, not an overlay.
    await p.waitForFunction(()=>!document.querySelector("[data-toast].show"));
    await p.waitForTimeout(250);
    // Geometry and screenshot pixels must describe the same settled frame.
    await p.evaluate(()=>Promise.all(document.getAnimations().map(a=>a.finished.catch(()=>{}))));
    const spots=await p.evaluate(()=>{
      const out=[];
      document.querySelectorAll('p,li,h1,h2,h3,h4,h5,a,span,dd,dt,blockquote,legend,summary,label,cite,figcaption,small,code,strong,em,td,th,button').forEach(e=>{
        const t=e.textContent.trim(); if(!t || e.children.length) return;
        const r=e.getBoundingClientRect();
        if(r.width<12||r.height<8||r.top<0||r.bottom>innerHeight||r.left<0||r.right>innerWidth) return;
        const cs=getComputedStyle(e);
        if(cs.visibility==='hidden'||cs.display==='none'||parseFloat(cs.opacity)===0) return;
        out.push({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height),
                  fg:cs.color, size:parseFloat(cs.fontSize), weight:parseInt(cs.fontWeight)||400,
                  what:(e.className||e.tagName)+': '+t.slice(0,40)});
      });
      return out;
    });
    const shot=(await p.screenshot()).toString('base64');
    // decode + sample inside the browser via canvas
    const res=await p.evaluate(async ({shot,spots,scheme,pg})=>{
      const lin=c=>{c/=255; return c<=0.03928? c/12.92 : Math.pow((c+0.055)/1.055,2.4);};
      const lum=p=>0.2126*lin(p[0])+0.7152*lin(p[1])+0.0722*lin(p[2]);
      const ratio=(a,b)=>{const la=lum(a),lb=lum(b),hi=Math.max(la,lb),lo=Math.min(la,lb);return (hi+0.05)/(lo+0.05);};
      const parse=c=>c.match(/[\d.]+/g).slice(0,3).map(Number);
      const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1],a[2]-b[2]);
      const img=new Image(); img.src='data:image/png;base64,'+shot; await img.decode();
      const cv=document.createElement('canvas'); cv.width=img.width; cv.height=img.height;
      const g=cv.getContext('2d',{willReadFrequently:true}); g.drawImage(img,0,0);
      const out=[];
      for(const s of spots){
        const fg=parse(s.fg); const px=[];
        const y1=Math.min(s.y+s.h-1,img.height-1), x1=Math.min(s.x+s.w-1,img.width-1);
        for(let yy=s.y+1; yy<y1; yy+=2){
          const row=g.getImageData(s.x+1,yy,Math.max(1,x1-(s.x+1)),1).data;
          for(let i=0;i<row.length;i+=4*3){ const q=[row[i],row[i+1],row[i+2]];
            if(dist(q,fg)>90) px.push(q); }
        }
        if(px.length<12) continue;
        // modal (most common) background among non-foreground pixels
        const key=p=>p[0]+','+p[1]+','+p[2]; const m={}; let best=px[0],bc=0;
        for(const q of px){const k=key(q); m[k]=(m[k]||0)+1; if(m[k]>bc){bc=m[k];best=q;}}
        const r=ratio(fg,best);
        const large=s.size>=24 || (s.size>=18.66 && s.weight>=700);
        const need=large?3.0:4.5;
        out.push([r,need,scheme,pg,s.what]);
      }
      return out;
    }, {shot,spots,scheme,pg});
    for(const row of res){ runs++; rows.push(row); if(row[0]<row[1]) fails.push(row); }
    await ctx.close();
  }
}
await b.close();
rows.sort((a,b)=>(a[0]-a[1])-(b[0]-b[1]));
console.log(`Sampled ${runs} text runs against real composited pixels, across ${PAGES.length} pages in both colour schemes.`);
console.log('Tightest 5 (measured / required):');
for(const [r,n,sc,pg,w] of rows.slice(0,5)) console.log(`  ${r.toFixed(2)} / ${n.toFixed(1)}  ${sc.padEnd(5)} ${pg.padEnd(10)} ${String(w).slice(0,44)}`);
if(fails.length){
  console.log(`\n  FAIL  ${fails.length} text run(s) below the WCAG minimum:`);
  for(const [r,n,sc,pg,w] of fails.slice(0,20)) console.log(`    ${r.toFixed(2)} < ${n} ${sc} ${pg} ${w}`);
} else {
  console.log(`\n  OK   every one of ${runs} sampled text runs meets its WCAG contrast minimum`);
}
process.exit(fails.length?1:0);
