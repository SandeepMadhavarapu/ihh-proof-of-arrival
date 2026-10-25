/* Immigrant Hall of Honor — Margin Notes and "Spot something? Tell us".
   Loaded only where notes are switched on. Settings come from data attributes on one
   container (data-ihh-notes = wordpress | email). The local demo adds its own adapter from
   voices/demo_adapter.js; that file is never part of site/. Visitor text is only ever written
   with textContent, never as HTML; nothing a visitor wrote becomes a link; emails are never
   shown. A curator approves every note before anyone else sees it. */
(function(){
  'use strict';
  var root = document.querySelector('[data-ihh-notes]');
  if (!root) return;
  var cfg = {
    adapter: root.getAttribute('data-ihh-notes'),
    page:    root.getAttribute('data-ihh-page') || '',
    api:     root.getAttribute('data-ihh-api') || '',
    wp:      (root.getAttribute('data-ihh-wp') || '').replace(/\/+$/, ''),
    post:    root.getAttribute('data-ihh-post') || '',
    email:   root.getAttribute('data-ihh-email') || ''
  };
  /* An adapter sends a submission (send) and may fetch approved notes (load). */
  var ADAPTERS = window.IHHVoicesAdapters || {};
  var adapter = ADAPTERS[cfg.adapter] || {wordpress: 1, email: 1}[cfg.adapter] && {};
  if (!adapter) return;
  var html = document.documentElement;
  html.classList.add('vv-js');
  if (root.getAttribute('data-ihh-scheme') === 'auto') html.classList.add('vv-dark-ok');

  var TYPES = [['perspective', 'My perspective'], ['more', 'I know more'],
               ['wrong', 'Something looks wrong'], ['question', 'Question']];
  var LABEL = {}; TYPES.forEach(function(t){ LABEL[t[0]] = t[1]; });
  var MAX = 1000, CONTEXT = 32;
  var CONFIRM = 'Thanks — a curator reviews every note before it appears.';
  var UNDER13 = 'If you are under 13, please don’t include your name, email, school or anything ' +
                'else that identifies you. Just tell us what you know.';
  var EMAIL = /[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+/g;

  function el(tag, cls, text){
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function norm(s){ return s.replace(/\s+/g, ' ').trim(); }
  function plainQuotes(s){ return s.replace(/[‘’]/g, "'").replace(/[“”]/g, '"'); }

  /* ── passages: same text voices/anchors.py sees (badges and note controls skipped) ── */
  var passages = [].slice.call(root.querySelectorAll('[data-ihh-anchor]'));
  function textNodes(p){
    var out = [], w = document.createTreeWalker(p, NodeFilter.SHOW_TEXT, null), n;
    while ((n = w.nextNode())){
      var par = n.parentNode.closest ? n.parentNode.closest('.vbadge,.vv-ui') : null;
      if (!par || !p.contains(par)) out.push(n);
    }
    return out;
  }
  function passageText(p){ return norm(textNodes(p).map(function(n){ return n.nodeValue; }).join('')); }
  function selectorFor(p, range){
    var nodes = textNodes(p), raw = '', s = -1, e = -1;
    nodes.forEach(function(n){
      if (n === range.startContainer) s = raw.length + range.startOffset;
      if (n === range.endContainer) e = raw.length + range.endOffset;
      raw += n.nodeValue;
    });
    if (s < 0 || e < 0 || e <= s) return null;
    var exact = norm(raw.slice(s, e));
    if (!exact) return null;
    return {type: 'TextQuoteSelector', exact: exact.slice(0, 600),
            prefix: norm(raw.slice(0, s)).slice(-CONTEXT), suffix: norm(raw.slice(e)).slice(0, CONTEXT)};
  }
  function wholeSelector(p){ return {type: 'TextQuoteSelector', exact: passageText(p).slice(0, 600), prefix: '', suffix: ''}; }

  /* ── where a note belongs: its id, else its quoted words (exact, unique) ── */
  function locate(anchor, sel){
    var byId = anchor && document.getElementById(anchor);
    if (byId && byId.hasAttribute('data-ihh-anchor')) return byId;
    var want = sel && sel.exact ? plainQuotes(norm(sel.exact)) : '';
    if (!want) return null;
    var hits = passages.filter(function(p){ return plainQuotes(passageText(p)).indexOf(want) !== -1; });
    return hits.length === 1 ? hits[0] : null;      // ambiguous or gone: not shown
  }

  /* ── rails: count + Add a note, floated into the passage's margin ── */
  function rail(p){
    var r = null;
    for (var c = p.firstElementChild; c; c = c.nextElementSibling) if (c.classList.contains('vv-rail')) { r = c; break; }
    if (!r){ r = el('span', 'vv-rail vv-ui'); p.insertBefore(r, p.firstChild); }
    return r;
  }
  var isVerify = !!document.querySelector('.claims');
  if (!isVerify) passages.forEach(function(p){
    var b = el('button', 'vv-add', 'Comment on this section');
    b.type = 'button';
    var words = passageText(p).split(' ').slice(0, 8).join(' ');
    b.setAttribute('aria-label', 'Comment on the section beginning: ' + words);
    b.addEventListener('click', function(){
      open({kind: 'note', anchor: p.id, selector: wholeSelector(p), quote: passageText(p), trigger: b});
    });
    rail(p).appendChild(b);
  });

  /* ── "Add a note on this" for highlighted text ── */
  var selBtn = el('button', 'vv-sel vv-ui', 'Comment on this');
  selBtn.type = 'button'; selBtn.hidden = true;
  var pending = null, selTimer = null;
  selBtn.addEventListener('mousedown', function(e){ e.preventDefault(); });   // keep the selection
  selBtn.addEventListener('click', function(){
    if (!pending) return;
    open({kind: 'note', anchor: pending.p.id, selector: pending.sel, quote: pending.sel.exact, trigger: selBtn});
  });
  function checkSelection(){
    var s = window.getSelection && window.getSelection();
    pending = null;
    if (s && s.rangeCount && !s.isCollapsed && !isVerify){
      var r = s.getRangeAt(0), c = r.commonAncestorContainer;
      var p = (c.nodeType === 1 ? c : c.parentNode).closest('[data-ihh-anchor]');
      if (p && root.contains(p) && !panel.contains(c)){
        var sel = selectorFor(p, r);
        if (sel){
          pending = {p: p, sel: sel};
          var rect = r.getBoundingClientRect();
          if (selBtn.parentNode !== p.parentNode || selBtn.previousElementSibling !== p) p.insertAdjacentElement('afterend', selBtn);
          selBtn.hidden = false;
          var host = selBtn.offsetParent ? selBtn.offsetParent.getBoundingClientRect() : {left: 0, top: 0};
          var left = Math.max(8, Math.min(rect.left - host.left, document.documentElement.clientWidth - host.left - 180));
          selBtn.style.left = left + 'px';
          selBtn.style.top = (rect.bottom - host.top + 6) + 'px';
          return;
        }
      }
    }
    if (document.activeElement !== selBtn) selBtn.hidden = true;
  }
  document.addEventListener('selectionchange', function(){ clearTimeout(selTimer); selTimer = setTimeout(checkSelection, 120); });

  /* ── the panel ── */
  var panel = el('div', 'vv-panel');
  panel.hidden = true;
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-labelledby', 'vv-title');
  var head = el('div', 'vv-head');
  var title = el('h2', null, 'Comment on this section'); title.id = 'vv-title'; title.tabIndex = -1;
  var x = el('button', 'vv-x', '×'); x.type = 'button'; x.setAttribute('aria-label', 'Close');
  head.appendChild(title); head.appendChild(x);
  var ctxL = el('p', 'vv-ctx-l', 'You are responding to:');
  var ctx = el('blockquote', 'vv-ctx');
  var form = el('form', 'vv-form'); form.noValidate = true;
  var fs = el('fieldset', 'vv-types'); fs.appendChild(el('legend', null, 'What kind of note is it?'));
  TYPES.forEach(function(t){
    var lab = el('label', 'vv-type'), r = el('input');
    r.type = 'radio'; r.name = 'vv-type'; r.value = t[0];
    lab.appendChild(r); lab.appendChild(document.createTextNode(t[1]));
    fs.appendChild(lab);
  });
  function field(id, label, opt, input){
    var lab = el('label', null, label); lab.htmlFor = id;
    if (opt) { lab.appendChild(document.createTextNode(' ')); lab.appendChild(el('span', 'vv-opt', opt)); }
    input.id = id;
    return [lab, input];
  }
  var verdictP = el('p', 'vv-verdict'); verdictP.hidden = true;
  var text = el('textarea'); text.maxLength = MAX; text.rows = 5; text.required = true;
  var count = el('p', 'vv-count'); count.id = 'vv-count'; text.setAttribute('aria-describedby', 'vv-count');
  var source = el('input'); source.type = 'text'; source.maxLength = 300;
  var srcWrap = el('div'); srcWrap.hidden = true;
  field('vv-source', 'Where did you learn this?', '(optional: a book, website or record)', source).forEach(function(n){ srcWrap.appendChild(n); });
  var kid = el('p', 'vv-kid', UNDER13); kid.id = 'vv-kid';
  var name = el('input'); name.type = 'text'; name.maxLength = 40; name.autocomplete = 'given-name';
  var email = el('input'); email.type = 'email'; email.maxLength = 120; email.autocomplete = 'email';
  name.setAttribute('aria-describedby', 'vv-kid'); email.setAttribute('aria-describedby', 'vv-kid');
  var hp = el('div', 'vv-hp'); hp.setAttribute('aria-hidden', 'true');
  var hpIn = el('input'); hpIn.type = 'text'; hpIn.tabIndex = -1; hpIn.autocomplete = 'off'; hpIn.name = 'website';
  field('vv-website', 'Leave this empty', '', hpIn).forEach(function(n){ hp.appendChild(n); });
  var err = el('p', 'vv-err'); err.setAttribute('role', 'alert'); err.hidden = true;
  var send = el('button', 'vv-send', 'Send to a curator'); send.type = 'submit';
  form.appendChild(fs); form.appendChild(verdictP);
  var textLabel = field('vv-text', 'Your note', '', text);
  textLabel.forEach(function(n){ form.appendChild(n); });
  form.appendChild(count); form.appendChild(srcWrap); form.appendChild(kid);
  field('vv-name', 'First name', '(optional, shown with your note)', name).forEach(function(n){ form.appendChild(n); });
  field('vv-email', 'Email', '(optional, never shown; only so a curator can reply)', email).forEach(function(n){ form.appendChild(n); });
  form.appendChild(hp); form.appendChild(err); form.appendChild(send);
  var done = el('p', 'vv-done'); done.setAttribute('role', 'status'); done.tabIndex = -1; done.hidden = true;
  [head, ctxL, ctx, form, done].forEach(function(n){ panel.appendChild(n); });
  document.body.appendChild(panel);

  function tick(){ count.textContent = text.value.length.toLocaleString() + ' of ' + MAX.toLocaleString() + ' characters'; }
  text.addEventListener('input', tick);
  fs.addEventListener('change', function(){
    var t = type(fs); srcWrap.hidden = !(t === 'more' || t === 'wrong');
  });
  function type(scope){ var r = scope.querySelector('input[type=radio]:checked'); return r ? r.value : ''; }

  var current = null;
  var VERDICT = {confirmed: 'Confirmed', unsupported: 'Not supported', contradicted: 'Contradicted'};
  function open(c){
    current = c;
    var finding = c.kind === 'finding';
    title.textContent = c.kind === 'claim' ? 'Report or add to this claim' :
                        finding ? 'Share your finding with the museum' : 'Comment on this section';
    ctxL.textContent = c.kind === 'note' ? 'You are responding to:' : 'The claim:';
    ctx.textContent = c.quote;
    form.reset(); tick(); err.hidden = true; done.hidden = true; form.hidden = false; send.disabled = false;
    srcWrap.hidden = true;
    fs.hidden = finding; verdictP.hidden = !finding; text.required = !finding;
    verdictP.textContent = finding ? 'Your finding: ' + VERDICT[c.verdict] : '';
    textLabel[0].firstChild.nodeValue = finding ? 'Why? ' : 'Your note';
    if (finding && !textLabel[0].querySelector('.vv-opt')) textLabel[0].appendChild(el('span', 'vv-opt', '(optional)'));
    if (!finding){ var o = textLabel[0].querySelector('.vv-opt'); if (o) o.remove(); }
    if (c.kind === 'claim'){ fs.querySelector('input[value=wrong]').checked = true; srcWrap.hidden = false; }
    panel.hidden = false;
    title.focus();
  }
  function close(){
    panel.hidden = true;
    var t = current && current.trigger;
    current = null;
    if (t && document.body.contains(t) && !t.hidden) t.focus();
  }
  x.addEventListener('click', close);
  document.addEventListener('keydown', function(e){
    if ((e.key === 'Escape' || e.key === 'Esc') && !panel.hidden){ e.preventDefault(); close(); }
  });

  /* ── sending: one shape, three adapters ── */
  var sent = [];
  function allowed(){
    var t = Date.now();
    sent = sent.filter(function(s){ return t - s < 600000; });
    return sent.length < 3;
  }
  function problem(p){
    if (p.kind === 'finding'){ if (!VERDICT[p.verdict]) return 'Record your finding first.'; }
    else if (!p.type) return 'Choose what kind of note this is.';
    if (!p.text && p.kind !== 'finding') return 'Write something first.';
    if (p.text.length > MAX) return 'Keep it under ' + MAX + ' characters.';
    if (p.email && !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(p.email)) return 'That email address does not look right. It is optional, so you can leave it empty.';
    return '';
  }
  function wpBody(p){
    var lines = ['[ihh-note v1 kind=' + p.kind + ' type=' + p.type + ' page=' + p.page + ' anchor=' + (p.anchor || '-') +
                 (p.verdict ? ' verdict=' + p.verdict : '') + ']'];
    if (p.selector && p.selector.exact){
      lines.push('Quote: ' + p.selector.exact);
      if (p.selector.prefix) lines.push('Before: ' + p.selector.prefix);
      if (p.selector.suffix) lines.push('After: ' + p.selector.suffix);
    }
    if (p.source) lines.push('Source: ' + p.source);
    if (p.relationship) lines.push('Relationship: ' + p.relationship);
    lines.push('=====', p.text);
    return lines.join('\n');
  }
  function deliver(p){
    if (adapter.send) return adapter.send(p, cfg).then(function(msg){ return msg || CONFIRM; });
    if (cfg.adapter === 'wordpress'){
      var body = new URLSearchParams();
      body.set('comment_post_ID', cfg.post); body.set('author', p.name); body.set('email', p.email);
      body.set('url', ''); body.set('comment', wpBody(p));
      return fetch(cfg.wp + '/wp-comments-post.php', {method: 'POST', body: body, credentials: 'same-origin', redirect: 'manual'})
        .then(function(r){ if (r.type === 'opaqueredirect' || r.ok) return CONFIRM; throw new Error('status ' + r.status); });
    }
    var subject = (p.kind === 'note' ? 'Note on ' : p.kind === 'finding' ? 'Finding on ' : 'Report on ') + p.page + (p.anchor ? ', ' + p.anchor : '');
    location.href = 'mailto:' + cfg.email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(wpBody(p));
    return Promise.resolve('Your email app should open with your note filled in. Once you send it: ' + CONFIRM);
  }
  function submit(p, ui){
    var why = problem(p);
    if (why){ ui.err.textContent = why; ui.err.hidden = false; ui.focusBad(); return; }
    ui.err.hidden = true;
    if (p.website){ ui.ok(CONFIRM); return; }        // honeypot: say thanks, send nothing
    if (!allowed()){ ui.err.textContent = 'You have sent several notes in the last few minutes. Please wait a little and try again.'; ui.err.hidden = false; return; }
    delete p.website;
    ui.busy(true);
    deliver(p).then(function(msg){ sent.push(Date.now()); ui.ok(msg); },
      function(){ ui.busy(false); ui.err.textContent = 'Sorry, that did not send. Please try again in a moment.'; ui.err.hidden = false; });
  }
  form.addEventListener('submit', function(e){
    e.preventDefault();
    if (!current) return;
    var p = {kind: current.kind, type: current.kind === 'finding' ? 'finding' : type(fs), page: cfg.page, anchor: current.anchor,
             selector: current.kind === 'claim' ? {} : current.selector, verdict: current.verdict || '', text: text.value.trim(),
             source: srcWrap.hidden ? '' : source.value.trim(), name: name.value.trim(), email: email.value.trim(),
             website: hpIn.value};
    submit(p, {err: err,
      focusBad: function(){ (p.type || p.kind === 'finding' ? text : fs.querySelector('input')).focus(); },
      busy: function(b){ send.disabled = b; send.textContent = b ? 'Sending…' : 'Send to a curator'; },
      ok: function(msg){ form.hidden = true; done.textContent = msg; done.hidden = false; done.focus(); }});
  });

  /* ── Verify page: a button on every claim, and the general form ── */
  [].slice.call(document.querySelectorAll('.cl')).forEach(function(cl){
    var box = cl.querySelector('.vv-claim');
    if (!box){ box = el('p', 'vv-claim'); cl.appendChild(box); }
    var b = el('button', 'vv-claim-btn', 'Report or add to this claim'); b.type = 'button';
    b.setAttribute('aria-label', 'Report or add to this claim: ' + (cl.getAttribute('data-case') || '') + ', claim ' + (cl.getAttribute('data-n') || ''));
    b.addEventListener('click', function(){
      var t = cl.querySelector('.cl-text');
      open({kind: 'claim', anchor: cl.id, quote: t ? norm(t.textContent) : '', trigger: b});
    });
    box.appendChild(b);
    /* Share my finding: the visitor's verdict, tied to this claim's id, with the claim quoted. */
    var share = el('button', 'vv-claim-btn vv-share', 'Share my finding with the museum'); share.type = 'button';
    share.hidden = true;
    share.setAttribute('aria-label', 'Share your finding on ' + (cl.getAttribute('data-case') || '') + ', claim ' + (cl.getAttribute('data-n') || ''));
    share.addEventListener('click', function(){
      var r = cl.querySelector('.vd input[type=radio]:checked'), t = cl.querySelector('.cl-text');
      if (!r) return;
      var q = t ? norm(t.textContent) : '';
      open({kind: 'finding', anchor: cl.id, verdict: r.value, quote: q,
            selector: {type: 'TextQuoteSelector', exact: q.slice(0, 600), prefix: '', suffix: ''}, trigger: share});
    });
    cl.addEventListener('change', function(e){ if (e.target.closest('.vd')) share.hidden = false; });
    if (cl.querySelector('.vd input[type=radio]:checked')) share.hidden = false;
    box.appendChild(share);
  });
  var tell = document.getElementById('vv-tell-form');
  if (tell){
    var tErr = tell.querySelector('.vv-err'), tSend = tell.querySelector('.vv-send');
    var tDone = document.getElementById('vv-tell-done');
    tell.hidden = false;      // hidden in the HTML unless a no-JS handler exists
    tell.addEventListener('submit', function(e){
      e.preventDefault();
      var v = function(n){ var f = tell.elements[n]; return f ? f.value.trim() : ''; };
      var p = {kind: 'tip', type: 'more', page: v('inductee'), anchor: '', selector: {}, text: v('text'),
               source: v('source'), relationship: v('relationship'), name: v('name'), email: v('email'),
               website: tell.elements.website ? tell.elements.website.value : ''};
      submit(p, {err: tErr,
        focusBad: function(){ tell.elements.text.focus(); },
        busy: function(b){ tSend.disabled = b; },
        ok: function(msg){ tell.hidden = true; tDone.textContent = msg; tDone.hidden = false; tDone.focus(); }});
    });
  }

  /* ── approved notes: margin counts and "Notes on this page" ── */
  function index(){
    var sec = document.querySelector('.vv-index');
    if (sec) return sec;
    sec = el('section', 'vv-index'); sec.id = 'notes'; sec.setAttribute('aria-labelledby', 'notes-h');
    var h = el('h2', null, 'Notes on this page'); h.id = 'notes-h';
    sec.appendChild(h);
    sec.appendChild(el('p', 'vv-lede', 'Notes left by visitors, in their own words. A curator reads every note before it appears. Notes are not checked facts; the page above is.'));
    sec.appendChild(el('ol', 'vv-list'));
    var prof = root.querySelector('.ihh-profile');
    (prof ? prof.parentNode : root).insertBefore(sec, prof ? prof.nextSibling : null);
    return sec;
  }
  /* Type label, first name and date: one header for every note and finding (as voices/render.py). */
  function meta(label, n){
    var m = el('p', 'vv-meta');
    m.appendChild(el('span', 'vv-type', label));
    m.appendChild(document.createTextNode(' · ' + (n.by || 'A visitor') + ' · '));
    var t = el('time', null, n.date || ''); if (n.date) t.setAttribute('datetime', n.date);
    m.appendChild(t);
    return m;
  }
  function clip(q){ return q.length > 300 ? q.slice(0, 300).replace(/\s+\S*$/, '') + '…' : q; }
  function exactOf(n){ return norm((n.selector && n.selector.exact) || ''); }
  function onPage(q, p){ return plainQuotes(passageText(p)).indexOf(plainQuotes(q)) !== -1; }
  /* The passage a thread quotes once: the first note's words still on the page, else the passage now. */
  function headerQuote(list, p){
    for (var i = 0; i < list.length; i++){ var q = exactOf(list[i]); if (q && onPage(q, p)) return q; }
    return passageText(p);
  }
  /* One note. If it answered other words than the thread quotes, it shows its own; if those words
     are no longer on the page, it says it was left on an earlier wording. */
  function noteItem(n, p, header){
    var item = el('li', 'vv-note'), q = exactOf(n);
    item.appendChild(meta(LABEL[n.type] || 'Note', n));
    if (p && q && !onPage(q, p)){
      item.appendChild(el('blockquote', 'vv-q vv-q-own', clip(q)));
      item.appendChild(el('p', 'vv-was', 'This comment was left on an earlier wording of the passage.'));
    } else if (header && q && q !== header){
      item.appendChild(el('blockquote', 'vv-q vv-q-own', clip(q)));
    }
    item.appendChild(el('p', 'vv-text', String(n.text || '').replace(EMAIL, '[email removed]')));
    return item;
  }
  function threadBody(list, p, cls){
    var frag = document.createDocumentFragment(), header = headerQuote(list, p);
    frag.appendChild(el('blockquote', 'vv-q', clip(header)));
    var ul = el('ul', cls);
    list.forEach(function(n){ ul.appendChild(noteItem(n, p, header)); });
    frag.appendChild(ul);
    return frag;
  }
  /* A count that expands, right under the passage it belongs to. */
  function thread(p, list){
    var k = list.length, d = el('details', 'vv-thread vv-ui'); d.id = 'vv-t-' + p.id;
    d.appendChild(el('summary', null, k + ' visitor comment' + (k > 1 ? 's' : '') + ' on this section'));
    d.appendChild(threadBody(list, p, 'vv-notes plain'));
    p.insertAdjacentElement('afterend', d);
  }
  function draw(notes){
    var placed = {}, order = [], general = [];
    notes.forEach(function(n){
      if (!n.anchor && !(n.selector && norm(n.selector.exact || ''))){ general.push(n); return; }   // legacy: never had a passage
      var p = locate(n.anchor, n.selector);
      if (!p) return;
      if (!placed[p.id]){ placed[p.id] = []; order.push(p); }
      placed[p.id].push(n);
    });
    order.sort(function(a, b){ return passages.indexOf(a) - passages.indexOf(b); });
    [].slice.call(root.querySelectorAll('.vv-mark, .vv-thread, .vv-general-wrap')).forEach(function(m){ m.remove(); });
    var sec = index(), list = sec.querySelector('.vv-list'), empty = sec.querySelector('.vv-empty');
    list.textContent = '';
    if (empty) empty.hidden = order.length > 0 || general.length > 0;
    order.forEach(function(p){ thread(p, placed[p.id]); });
    order.forEach(function(p){
      var k = placed[p.id].length;
      var m = el('a', 'vv-mark', String(k)); m.href = '#vv-' + p.id;
      m.appendChild(el('span', 'vv-sr', ' visitor note' + (k > 1 ? 's' : '') + ' on this passage'));
      var r = rail(p); r.insertBefore(m, r.firstChild);
      var li = el('li', 'vv-entry'); li.id = 'vv-' + p.id;
      li.appendChild(threadBody(placed[p.id], p, 'vv-notes'));
      var back = el('p', 'vv-back'), a = el('a', null, 'Back to the passage'); a.href = '#' + p.id;
      back.appendChild(a); li.appendChild(back);
      list.appendChild(li);
    });
    if (general.length){
      var wrap = el('div', 'vv-general-wrap');
      wrap.appendChild(el('h3', 'vv-general-h', 'General notes on this page'));
      wrap.appendChild(el('p', 'vv-lede', 'Older notes that were not left on a particular section.'));
      var g = el('ul', 'vv-notes vv-general');
      general.forEach(function(n){ g.appendChild(noteItem(n)); });
      wrap.appendChild(g);
      sec.appendChild(wrap);
    }
  }
  /* Verify: approved findings under their claim, as a tally that expands. */
  function drawFindings(list){
    var by = {};
    list.forEach(function(f){ if (VERDICT[f.verdict] && document.getElementById(f.anchor)) (by[f.anchor] = by[f.anchor] || []).push(f); });
    [].slice.call(document.querySelectorAll('.cl .vv-findings')).forEach(function(d){ d.remove(); });
    Object.keys(by).forEach(function(id){
      var cl = document.getElementById(id), fs = by[id], counts = [];
      Object.keys(VERDICT).forEach(function(v){
        var k = fs.filter(function(f){ return f.verdict === v; }).length;
        if (k) counts.push(k + ' ' + VERDICT[v]);
      });
      var d = el('details', 'vv-thread vv-findings'); d.id = 'vv-t-' + id;
      d.appendChild(el('summary', null, fs.length + ' visitor finding' + (fs.length > 1 ? 's' : '') + ': ' + counts.join(' · ')));
      var ul = el('ul', 'vv-notes plain'), cur = norm((cl.querySelector('.cl-text') || {}).textContent || '');
      fs.forEach(function(f){
        var item = el('li', 'vv-note');
        item.appendChild(meta('My finding: ' + VERDICT[f.verdict], f));
        if (f.text) item.appendChild(el('p', 'vv-text', String(f.text).replace(EMAIL, '[email removed]')));
        var was = norm((f.selector && f.selector.exact) || '');
        if (was && was !== cur) item.appendChild(el('p', 'vv-was', 'Shared on an earlier wording of this claim.'));
        ul.appendChild(item);
      });
      d.appendChild(ul);
      var box = cl.querySelector('.vv-claim');
      cl.insertBefore(d, box || null);
    });
  }
  function firstName(s){
    var w = String(s || '').trim().split(/\s+/)[0] || '';
    w = w.replace(/[^\w'\-À-ɏ]/g, '');
    return w && !/@/.test(s) ? w.slice(0, 20) : 'A visitor';
  }
  function fromWordPress(c){
    var raw = String((c.content && c.content.rendered) || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/p>/gi, '\n');
    var txt = new DOMParser().parseFromString(raw, 'text/html').body.textContent || '';
    var m = txt.match(/\[ihh-note v1 kind=(\w+) type=(\w+) page=([a-z0-9-]+) anchor=([a-z0-9-]+)\]/);
    if (!m || m[1] !== 'note' || !LABEL[m[2]]) return null;
    var parts = txt.split(/\n=====\n/), headLines = parts[0].split('\n'), sel = {exact: ''};
    headLines.forEach(function(l){ if (l.indexOf('Quote: ') === 0) sel.exact = l.slice(7); });
    return {type: m[2], anchor: m[4], selector: sel, text: parts.slice(1).join('\n').trim(),
            by: firstName(c.author_name), date: String(c.date || '').slice(0, 10)};
  }
  if (isVerify){
    if (adapter.load) adapter.load(cfg).then(function(list){ drawFindings((list || []).filter(function(f){ return f.kind === 'finding'; })); }, function(){});
  } else {
    if (adapter.load){
      adapter.load(cfg).then(function(notes){ draw(notes || []); }, function(){});
    } else if (cfg.adapter === 'wordpress' && cfg.post){
      fetch(cfg.wp + '/wp-json/wp/v2/comments?post=' + encodeURIComponent(cfg.post) + '&per_page=100', {credentials: 'omit'})
        .then(function(r){ return r.ok ? r.json() : []; })
        .then(function(list){ var n = (list || []).map(fromWordPress).filter(Boolean); if (n.length) draw(n); }, function(){});
    }
  }
})();
