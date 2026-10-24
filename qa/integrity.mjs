import { IND, ORIGINAL } from './catalog.mjs';
import { readFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';
/* Static integrity checks on the SHIPPED files. No browser needed.
   Run: node qa/integrity.mjs <package-root> */
const ROOT = process.argv[2] || '.';
const pass=[],fail=[]; const ck=(c,m)=>(c?pass:fail).push(m);
const site=join(ROOT,'site'), wpOf=n=>join(ROOT,'inductees',n);
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

/* generated profile pages: no script inside the profile, every image has alt text and a credit */
for (const n of IND){
  const pg=read(join(site,n+'.html'));
  const prof=pg.slice(pg.indexOf('<div class="ihh-profile">'), pg.indexOf('</main>'));
  ck(!prof.includes('<script'), n+'.html: no script inside the profile');
  const imgs=[...prof.matchAll(/<img [^>]*>/g)].map(m=>m[0]);
  ck(imgs.length>0 && imgs.every(t=>/alt="[^"]{10,}"/.test(t)), n+'.html: all '+imgs.length+' images have alt text');
  ck(/<figcaption>[\s\S]*?Rights, in the institution/.test(prof), n+'.html: anchor image carries its rights wording');
}

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

/* the WordPress deliverables: one package per inductee in inductees/<name>/ */
const splitCsv = line => {
  const out=[]; let cur='', q=false;
  for (const ch of line){
    if (ch === '"') { q=!q; continue; }
    if (ch === ',' && !q) { out.push(cur); cur=''; continue; }
    cur += ch;
  }
  out.push(cur); return out;
};
const parseCsv = txt => {           // tolerant of quoted newlines
  const rows=[]; let cur='', q=false;
  for (const ch of txt){ if(ch==='"') q=!q; if(ch==='\n' && !q){ rows.push(cur); cur=''; } else cur+=ch; }
  if(cur.trim()) rows.push(cur); return rows.filter(row=>row.trim()).map(row=>splitCsv(row.replace(/\r$/, "")));
};
for (const n of IND){
  const wp=wpOf(n);
  const cp=read(join(wp,'copy.html'));
  ck(!/<script/i.test(cp), n+': WordPress fragment contains zero script tags');
  ck(!/<link\b|@import|fonts\.googleapis|cdn\./i.test(cp), n+': fragment loads no external resource');
  if (ORIGINAL.includes(n)) ck((cp.match(/class="src-item"/g)||[]).length>=10, n+': original fragment retains 10+ source items');
  const hasLog=existsSync(join(wp,'search-log.csv'));
  if (ORIGINAL.includes(n)) ck(hasLog, n+': original search log present');
  else ck(hasLog || read(join(ROOT,'handover','OPEN-ITEMS.md')).split('## '+n.charAt(0).toUpperCase()+n.slice(1)+'\n')[1]?.split('\n## ')[0].includes('**MISSING SEARCH LOG: search-log.csv.**'), n+': missing research log explicitly reported');
  const rows=parseCsv(read(join(wp,'media-manifest.csv'))); const hdr=rows[0];
  const col=k=>hdr.indexOf(k);
  const included=rows.slice(1).filter(r=>!/^DROP/i.test(r[col('recommendation')]||''));
  ck(included.length>0 && (cp.match(/class="src-item"/g)||[]).length===included.length, n+': every non-dropped manifest row rendered exactly once');
  /* alt text limits — actually parsed. Cooper Hewitt <=15 words; AAM <=125 chars. */
  let altBad=[], altSeen=0;
  for (const r of rows.slice(1)){
    const alt=(r[col('alt_text')]||'').trim(); if(!alt) continue; altSeen++;
    const words=alt.split(/\s+/).length;
    if(alt.length>125 || words>15) altBad.push(alt.slice(0,34)+` (${alt.length}ch/${words}w)`);
  }
  ck(altSeen>0, n+': manifest alt_text column parsed ('+altSeen+' values)');
  ck(altBad.length===0, n+': every alt text <=15 words and <=125 chars'+(altBad.length?' — '+JSON.stringify(altBad):''));
  /* every image row the page uses was looked at by a person, not described from metadata */
  const unviewed=rows.slice(1).filter(r=>/\.(jpe?g|png|tif)$/i.test(r[col('filename')]) && !/DROP/.test(r[col('recommendation')]) && !/VIEWED/.test(r[col('status')]));
  ck(unviewed.length===0, n+': every image used was viewed before it was described'+(unviewed.length?' — '+unviewed.map(r=>r[0]).join(','):''));
  /* no <img> in the deliverable may point at a file the package does not contain */
  const liveImgs=[...cp.matchAll(/<img[^>]+src="media\/web\/([^"]+)"/g)].map(m=>m[1]);
  const have=existsSync(join(wp,'media','web'))?readdirSync(join(wp,'media','web')):[];
  const dangling=liveImgs.filter(f=>!have.includes(f));
  ck(liveImgs.length>0 && dangling.length===0, n+': all '+liveImgs.length+' images present in media/web'+(dangling.length?' — '+JSON.stringify(dangling):''));
}
ck(read(join(wpOf('albright'),'media-manifest.csv')).includes('DUPLICATE'), "albright: manifest preserves the commission's duplicate identification");
ck(existsSync(join(ROOT,'handover','INSTALL.md')), 'handover/INSTALL.md present');

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

/* generators must be path-portable */
for (const g of [join(site,'gen.py'), join(ROOT,'tools','build_profile.py'), join(ROOT,'tools','build_site_pages.py')]){
  ck(!/\/home\/claude/.test(read(g)), 'no absolute build-machine path in '+g.split('/').pop());
}
pass.forEach(m=>console.log('  OK   '+m));
if(fail.length){console.log(''); fail.forEach(m=>console.log('  FAIL '+m));
  console.log('\n'+fail.length+' FAILED of '+(pass.length+fail.length)); process.exit(1);}
console.log('\nALL '+pass.length+' INTEGRITY CHECKS PASSED');
