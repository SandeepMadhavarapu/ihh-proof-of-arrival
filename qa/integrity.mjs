import { readFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';
/* Static integrity checks on the SHIPPED files. No browser needed.
   Run: node qa/integrity.mjs <package-root> */
const ROOT = process.argv[2] || '.';
const pass=[],fail=[]; const ck=(c,m)=>(c?pass:fail).push(m);
const site=join(ROOT,'site'), wp=join(ROOT,'albright-wp');
const html = readdirSync(site).filter(f=>f.endsWith('.html'));
const read = p => readFileSync(p,'utf8');

/* privacy */
let formsWithGet=[];
for (const f of html){
  const s=read(join(site,f));
  for (const m of s.matchAll(/<form\b[^>]*>([\s\S]*?)<\/form>/gi)){
    const tag=m[0].match(/<form\b[^>]*>/i)[0];
    const body=m[1];
    const hasPost=/method\s*=\s*["']?post/i.test(tag);
    /* a GET form is a leak only if it actually collects personal data */
    const personal=/<(?:input|textarea|select)\b[^>]*\bname\s*=\s*["']?(?:e-?mail|mail|name|fname|lname|firstname|lastname|phone|tel|mobile|address|street|city|state|story|message|msg|comment|zip|postal|dob|ssn)\b/i.test(body);
    if(!hasPost && personal) formsWithGet.push(f+' :: '+tag.slice(0,70));
  }
}
ck(formsWithGet.length===0, 'no form can submit personal data by GET '+(formsWithGet.length?JSON.stringify(formsWithGet):''));
ck(!read(join(site,'share.html')).includes('<input'), 'the story page collects nothing');

/* no misleading dead links */
let hashLinks=0;
for (const f of html) hashLinks += (read(join(site,f)).match(/href="#"/g)||[]).length;
ck(hashLinks===0, 'no href="#" placeholder links ('+hashLinks+')');

/* sitemap must not claim the real museum's domain */
const sm=read(join(site,'sitemap.xml'));
const locs=[...sm.matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>m[1]);
ck(!locs.some(u=>u.includes('immigranthallofhonor.org')), 'no sitemap <loc> asserts the live museum domain');
ck(locs.every(u=>/^https?:\/\//.test(u)), 'every sitemap <loc> is an absolute URL as the spec requires');
ck(locs.length===html.length-1, 'sitemap lists every page except 404 ('+(sm.match(/<loc>/g)||[]).length+' vs '+(html.length-1)+')');

/* citation export uses defined RIS tags */
const alb=read(join(site,'albright.html'));
ck(!alb.includes("'TY  - ARCHIVE'"), 'RIS no longer emits an undefined type tag');
ck(alb.includes("'TY  - GEN'"), 'RIS emits a defined type tag');

/* withdrawn claim must not survive as an assertion anywhere */
for (const f of [...html.map(x=>join(site,x)), join(site,'FINDINGS.md')]){
  const s=read(f);
  let bad=false;
  for(const m of s.matchAll(/two contradictory copyright regimes/gi)){
    const ctx=s.slice(Math.max(0,m.index-450), m.index+450);
    if(!/withdraw|WITHDRAWN|previously|no longer true|refut/i.test(ctx)){bad=true;break;}
  }
  ck(!bad, 'no un-retracted copyright claim in '+f.split('/').pop());
}

/* the WordPress deliverable */
const cp=read(join(wp,'copy.html'));
ck(!/<script/i.test(cp), 'WordPress fragment contains zero script tags');
ck(!/<link\b|@import|fonts\.googleapis|cdn\./i.test(cp), 'fragment loads no external resource');
ck((cp.match(/class="src-item"/g)||[]).length>=10, 'fragment has 10+ source items');
ck(existsSync(join(wp,'INSTALL.md')), 'INSTALL.md present');
ck(existsSync(join(wp,'media-manifest.csv')), 'media-manifest.csv present');
ck(existsSync(join(wp,'media','fetch-media.sh')), 'media fetch script present');

/* the manifest must not understate what is missing */
const man=read(join(wp,'media-manifest.csv'));
ck(man.includes('NOT DOWNLOADED'), 'manifest states which files are absent');
ck(man.includes('METADATA-DERIVED'), 'manifest marks unverified long descriptions');
ck(man.includes('DUPLICATE'), "manifest preserves the commission's duplicate identification");
ck(man.includes('NOT READ'), 'manifest marks the document nobody opened');

/* alt text limits — actually parsed. Cooper Hewitt <=15 words; AAM <=125 chars.
   The previous version here was a dead loop followed by ck(true, ...), i.e. an
   unconditional pass reported as a real check. */
const csvRows = man.split('\n').filter(Boolean);
const hdr = csvRows[0].split(',');
const altIdx = hdr.indexOf('alt_text');
const splitCsv = line => {
  const out=[]; let cur='', q=false;
  for (const ch of line){
    if (ch === '"') { q=!q; continue; }
    if (ch === ',' && !q) { out.push(cur); cur=''; continue; }
    cur += ch;
  }
  out.push(cur); return out;
};
let altBad=[], altSeen=0;
for (const line of csvRows.slice(1)){
  const alt=(splitCsv(line)[altIdx]||'').trim();
  if(!alt) continue;
  altSeen++;
  const words=alt.split(/\s+/).length;
  if(alt.length>125 || words>15) altBad.push(alt.slice(0,34)+` (${alt.length}ch/${words}w)`);
}
ck(altSeen>0, 'manifest alt_text column parsed ('+altSeen+' values)');
ck(altBad.length===0, 'every alt text <=15 words and <=125 chars'+(altBad.length?' — '+JSON.stringify(altBad):''));

/* the site weight stated in prose must match the bytes actually shipped */
let wbytes=0;
const walk=d=>{ for(const e of readdirSync(d,{withFileTypes:true})){
  const fp=join(d,e.name);
  if(e.isDirectory()) walk(fp);
  else if(/\.(html|css|js|txt|xml)$/.test(e.name)) wbytes+=readFileSync(fp).length; } };
walk(site);
const trueKB=Math.floor(wbytes/1024);
const claimed=new Set();
for (const f of ['FINDINGS.md','SITE-README.md','TESTS-RUN.md','method.html']){
  const fp=join(site,f); if(!existsSync(fp)) continue;
  for (const m of read(fp).matchAll(/(?<![\d,])(\d{2,4})(?:&nbsp;|\s)KB/g)) claimed.add(Number(m[1]));
}
/* 2869 is the measured weight of the LIVE IHH homepage, quoted for comparison; it is not
   a claim about this package. Excluded by name rather than silently. */
const COMPARATORS=[2869];
const wrong=[...claimed].filter(k=>!COMPARATORS.includes(k) && Math.abs(k-trueKB)>2);
ck(claimed.size>0, 'site weight is stated in the documentation ('+[...claimed].join(', ')+' KB found)');
ck(wrong.length===0, 'every stated site weight matches the shipped bytes ('+trueKB+' KB)'+(wrong.length?' — stale: '+JSON.stringify(wrong):''));

/* no <img> in the deliverable may point at a file the package does not contain */
const liveImgs=[...cp.replace(/<!--[\s\S]*?-->/g,'').matchAll(/<img[^>]+src="media\/([^"]+)"/g)].map(m=>m[1]);
const haveMedia=existsSync(join(wp,'media'))?readdirSync(join(wp,'media')):[];
const dangling=liveImgs.filter(f=>!haveMedia.includes(f));
ck(dangling.length===0, 'no live <img> points at a missing file'+(dangling.length?' — '+JSON.stringify(dangling):''));

/* generators must be path-portable */
for (const g of [join(site,'gen.py'), join(wp,'build.py')]){
  ck(!/\/home\/claude/.test(read(g)), 'no absolute build-machine path in '+g.split('/').pop());
}
pass.forEach(m=>console.log('  OK   '+m));
if(fail.length){console.log(''); fail.forEach(m=>console.log('  FAIL '+m));
  console.log('\n'+fail.length+' FAILED of '+(pass.length+fail.length)); process.exit(1);}
console.log('\nALL '+pass.length+' INTEGRITY CHECKS PASSED');
