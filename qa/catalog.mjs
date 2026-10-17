import { readdirSync, existsSync, readFileSync } from 'node:fs';
export const IND = readdirSync('inductees').filter(n => existsSync(`inductees/${n}/copy.md`)).sort();
export const PAGES = readdirSync('site').filter(n => n.endsWith('.html')).map(n => n.slice(0,-5)).sort();
export const ORIGINAL = ['albright','lamarr','pei','cruz'];
export function expected(n) {
  const md=readFileSync(`inductees/${n}/copy.md`,'utf8');
  return {quotes: /\*\*Quotation:\*\*/.test(md)?1:0};
}
