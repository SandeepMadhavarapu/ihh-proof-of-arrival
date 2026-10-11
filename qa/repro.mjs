import { chromium } from 'playwright';
const U='http://127.0.0.1:8731/';
const b=await chromium.launch({executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const R=[];
const say=(id,verdict,detail)=>R.push({id,verdict,detail});

/* A + B — no JavaScript, phone width */
let ctx=await b.newContext({javaScriptEnabled:false,viewport:{width:375,height:812}});
let p=await ctx.newPage(); await p.goto(U+'albright.html');
const nojs=await p.evaluate(()=>({
  nav:getComputedStyle(document.querySelector('#nav')).display,
  menuBtn:getComputedStyle(document.querySelector('.menu-btn')).display,
  paras:[...document.querySelectorAll('.hero-copy p')].map(e=>({t:e.textContent.trim().slice(0,30),o:getComputedStyle(e).opacity})),
  fadeCount:document.querySelectorAll('.fade-up').length}));
say('A  no-JS hero paragraph invisible', nojs.paras.some(x=>x.o==='0')?'CONFIRMED':'not reproduced',
    JSON.stringify(nojs.paras)+'  (.fade-up elements on page: '+nojs.fadeCount+')');
say('B  no-JS mobile nav unreachable', (nojs.nav==='none')?'CONFIRMED':'not reproduced',
    'nav display='+nojs.nav+'; menu button is displayed but its only handler is JS');
await ctx.close();

/* C — dark mode pressed button */
ctx=await b.newContext({colorScheme:'dark',viewport:{width:1280,height:900}});
p=await ctx.newPage(); await p.goto(U+'albright.html');
await p.getByRole('button',{name:'Show the evidence',exact:true}).click();
const dk=await p.evaluate(()=>{
  const el=document.querySelector('.ihh .bar button[aria-pressed="true"]');
  const cs=getComputedStyle(el);
  const lum=c=>{const v=c.match(/\d+/g).slice(0,3).map(Number).map(n=>{n/=255;return n<=0.03928?n/12.92:Math.pow((n+0.055)/1.055,2.4)});
    return 0.2126*v[0]+0.7152*v[1]+0.0722*v[2];};
  const L1=lum(cs.color), L2=lum(cs.backgroundColor);
  const hi=Math.max(L1,L2), lo=Math.min(L1,L2);
  return {fg:cs.color,bg:cs.backgroundColor,ratio:+(((hi+0.05)/(lo+0.05)).toFixed(2)),label:el.textContent.trim()};});
say('C  dark pressed-button contrast', dk.ratio<4.5?'CONFIRMED':'not reproduced',
    '"'+dk.label+'" '+dk.fg+' on '+dk.bg+' = '+dk.ratio+':1, needs 4.5:1');
await ctx.close();

/* D + E — exhibit modal keyboard behaviour */
ctx=await b.newContext({viewport:{width:1280,height:900}});
p=await ctx.newPage(); await p.goto(U+'albright.html');
await p.getByRole('button',{name:'Exhibit mode',exact:true}).click(); await p.waitForTimeout(250);
await p.getByRole('button',{name:'Close (Esc)',exact:true}).focus();
await p.keyboard.press('Space'); await p.waitForTimeout(250);
const sp=await p.evaluate(()=>({open:document.querySelector('.ihh-stage').classList.contains('on'),
  count:((document.querySelector('.ihh-stage .count')||{}).textContent||'').trim()}));
say('D  Space on "Close" advances instead', sp.open?'CONFIRMED':'not reproduced',
    'modal still open='+sp.open+'; counter reads "'+sp.count+'"');
await p.keyboard.press('Escape'); await p.waitForTimeout(200);
await p.getByRole('button',{name:'Exhibit mode',exact:true}).click(); await p.waitForTimeout(250);
await p.keyboard.press('Shift+Tab'); await p.waitForTimeout(200);
const st=await p.evaluate(()=>({tag:document.activeElement.tagName,
  text:(document.activeElement.textContent||'').trim().slice(0,38),
  inside:!!document.activeElement.closest('.ihh-stage')}));
say('E  Shift+Tab escapes the modal', !st.inside?'CONFIRMED':'not reproduced',
    'focus landed on <'+st.tag+'> "'+st.text+'"; inside modal='+st.inside);
await ctx.close();

/* F — citation radios outside the first case file */
ctx=await b.newContext({viewport:{width:1280,height:900}});
p=await ctx.newPage(); await p.goto(U+'verify.html');
await p.locator('#h1 input[value=contradicted]').check();
await p.locator('#h1 .cite input[value="0"]').check(); await p.waitForTimeout(150);
const firstWorks=(await p.textContent('#sheet-body')).includes('none of the evidence');
await p.locator('#e1 input[value=contradicted]').check();
await p.locator('#e1 .cite input[value="0"]').check(); await p.waitForTimeout(150);
const n=((await p.textContent('#sheet-body')).match(/none of the evidence/g)||[]).length;
say('F  citation ignored outside case file 1', n<2?'CONFIRMED':'not reproduced',
    'case file 1 citation registered='+firstWorks+'; citations shown after recording two='+n+' (expected 2)');
await ctx.close();

/* G — Enter in the search field */
ctx=await b.newContext({viewport:{width:1280,height:900}});
p=await ctx.newPage(); await p.goto(U+'inductees.html');
await p.locator('#q').fill('Vienna'); await p.waitForTimeout(150);
const before=(await p.textContent('#count')).trim();
await p.locator('#q').press('Enter'); await p.waitForLoadState('load'); await p.waitForTimeout(300);
const after=(await p.textContent('#count')).trim();
say('G  Enter wipes search and filters', before!==after?'CONFIRMED':'not reproduced',
    '"'+before+'"  ->  "'+after+'"   url'+p.url().replace(/^http:\/\/[^/]+/,''));
await ctx.close();

/* H — hero layout at 320px */
ctx=await b.newContext({viewport:{width:320,height:900}});
p=await ctx.newPage(); await p.goto(U+'albright.html'); await p.waitForTimeout(300);
const h=await p.evaluate(()=>{const g=s=>{const e=document.querySelector(s);const r=e.getBoundingClientRect();
  return {x:Math.round(r.x),w:Math.round(r.width)};};
  return {copy:g('.hero-copy'),cap:g('.anchor figcaption')};});
say('H  hero text column at 320px', h.copy.w<220?'CONFIRMED':'not reproduced',
    'hero copy column '+h.copy.w+'px wide; figcaption '+h.cap.w+'px at x='+h.cap.x);
await ctx.close();

/* I — stacking: does a loaded hero image cover the credit line? */
ctx=await b.newContext({viewport:{width:1280,height:900}});
p=await ctx.newPage();
const PX='iVBORw0KGgoAAgAAAAgAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
await p.route('**/media/*.jpg', r=>r.fulfill({status:200,contentType:'image/png',
  body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==','base64')}));
await p.goto(U+'albright.html'); await p.waitForTimeout(500);
const stack=await p.evaluate(()=>{
  const cred=document.querySelector('.anchor .credit'); if(!cred) return {err:'no credit element'};
  const r=cred.getBoundingClientRect();
  const top=document.elementsFromPoint(r.x+4, Math.min(innerHeight-1, r.y+4)).slice(0,4)
    .map(e=>e.tagName+(typeof e.className==='string'&&e.className?'.'+e.className.split(' ')[0]:''));
  return {creditVisible:getComputedStyle(cred).visibility, rect:{x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width)}, top};});
say('I  loaded photo covers the hero credit', (stack.top&&stack.top[0]==='IMG')?'CONFIRMED':'not reproduced',
    'topmost element over the credit line: '+JSON.stringify(stack.top)+'  (test used a 1px stand-in image, so this measures stacking only)');
await ctx.close();
await b.close();

const w=Math.max(...R.map(r=>r.id.length));
R.forEach(r=>console.log((r.verdict==='CONFIRMED'?'  CONFIRMED  ':'  NOT REPRO  ')+r.id.padEnd(w)+'\n               '+r.detail+'\n'));
console.log('Reproduced '+R.filter(r=>r.verdict==='CONFIRMED').length+' of '+R.length+' findings.');
process.exit(R.some(r=>r.verdict==='CONFIRMED')?1:0);
