import { chromium } from 'playwright';
/* The exhibit scopes all of its own CSS under .ihh, but the site theme's rules are
   unscoped — so any class name they share leaks in. This measures which ones
   actually change rendering inside the exhibit. */
const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const ctx=await b.newContext({viewport:{width:1280,height:900}});
const p=await ctx.newPage();
await p.goto('http://127.0.0.1:8731/albright.html',{waitUntil:'load'});
await p.waitForTimeout(300);

const PROPS=['textAlign','borderTopWidth','borderLeftWidth','display','fontSize','fontStyle',
             'paddingTop','paddingLeft','marginTop','color','textTransform','letterSpacing'];
const snap=async()=>p.evaluate((PROPS)=>{
  const out={};
  /* Two classes are DELIBERATELY shared with the site theme, so the theme styling them
     is correct, not a leak. Anything else that changes is a real leak. The allowlist is
     named here rather than hidden in a selector so it stays reviewable:
       .skip  the skip link, so it matches every other page
       .todo  the site-wide marker for a slot a human must fill in         */
  const ALLOW = ['skip','todo'];
  document.querySelectorAll('.ihh [class]').forEach((e,i)=>{
    const cls = typeof e.className==='string' ? e.className.split(/\s+/) : [];
    if (cls.some(c=>ALLOW.includes(c))) return;
    const cs=getComputedStyle(e);
    out[i+'|'+e.tagName+'.'+e.className] = PROPS.map(k=>cs[k]).join('~');
  });
  return out;
},PROPS);

const withTheme=await snap();
const nDisabled=await p.evaluate(()=>{const ls=[...document.querySelectorAll("link[rel=stylesheet]")].filter(l=>/site\.css/.test(l.href)); ls.forEach(l=>l.disabled=true); return ls.length;});
if(!nDisabled){ console.log("LEAK TEST INVALID: could not find/disable the site stylesheet"); await b.close(); process.exit(1); }
await p.waitForTimeout(200);
const without=await snap();

const changed={};
for(const k of Object.keys(withTheme)){
  if(!(k in without)) continue;
  if(withTheme[k]!==without[k]){
    const cls=k.split('|')[1];
    const a=withTheme[k].split('~'), bb=without[k].split('~');
    const diffs=PROPS.map((n,i)=>a[i]!==bb[i]?n+': '+bb[i]+' -> '+a[i]:null).filter(Boolean);
    (changed[cls]=changed[cls]||new Set()); diffs.forEach(d=>changed[cls].add(d));
  }
}
const keys=Object.keys(changed);
if(!keys.length) console.log('No site-theme rule changes rendering inside the exhibit.');
else{
  console.log('Theme rules leaking into the .ihh exhibit:\n');
  keys.forEach(k=>{ console.log('  '+k); [...changed[k]].slice(0,4).forEach(d=>console.log('      '+d)); });
  console.log('\nLEAKS: '+keys.length+' element classes affected');
}
await b.close();
process.exit(keys.length?1:0);
