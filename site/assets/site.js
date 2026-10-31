/* Immigrant Hall of Honor — progressive enhancement only.
   Every page is complete and usable with this file removed. */
(function(){
  'use strict';

  /* Tell the stylesheet a script is running. Anything hidden behind `.js`
     is visible without it — nothing is gated on JavaScript. */
  if (!/(^| )js( |$)/.test(document.documentElement.className))
    document.documentElement.className += ' js';

  /* ── mobile menu ──────────────────────────────────────────────────── */
  var btn = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function(){
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
      btn.textContent = open ? 'Close' : 'Menu';
    });
  }

  /* ── inductee search + filters ────────────────────────────────────── */
  var list = document.querySelector('.cards');
  if (list) {
    var cards  = [].slice.call(list.querySelectorAll('.card'));
    var q      = document.getElementById('q');
    var count  = document.getElementById('count');
    var clear  = document.getElementById('clear');
    var boxes  = [].slice.call(document.querySelectorAll('.filters input[type=checkbox]'));

    function checked(name){
      return boxes.filter(function(b){ return b.name===name && b.checked; })
                  .map(function(b){ return b.value; });
    }
    function apply(){
      var term = (q && q.value || '').trim().toLowerCase();
      var R = checked('region'), D = checked('decade'), F = checked('field');
      var shown = 0;
      cards.forEach(function(c){
        var ok = true;
        if (R.length && R.indexOf(c.dataset.region)  === -1) ok = false;
        if (D.length && D.indexOf(c.dataset.decade)  === -1) ok = false;
        if (F.length && F.indexOf(c.dataset.field)   === -1) ok = false;
        if (ok && term) {
          var hay = (c.dataset.name || '') + ' ' + c.textContent.toLowerCase();
          if (hay.indexOf(term) === -1) ok = false;
        }
        c.hidden = !ok;
        if (ok) shown++;
      });
      if (count) {
        count.textContent = shown === cards.length
          ? 'Showing all ' + cards.length + '.'
          : (shown === 0
              ? 'Nothing matches those filters. Try clearing one.'
              : 'Showing ' + shown + ' of ' + cards.length + '.');
      }
    }
    /* Enter in the search field used to submit the form, reload the page and
       throw away every filter the visitor had set. */
    var form = list.closest ? document.querySelector('form.filters') : null;
    if (form) form.addEventListener('submit', function(e){ e.preventDefault(); apply(); });
    if (q) q.addEventListener('input', apply);
    boxes.forEach(function(b){ b.addEventListener('change', apply); });
    if (clear) clear.addEventListener('click', function(){
      boxes.forEach(function(b){ b.checked = false; });
      if (q) q.value = '';
      apply();
      if (q) q.focus();
    });
    apply();
  }

  /* ── story character counter ──────────────────────────────────────── */
  var story = document.getElementById('story'), counter = document.getElementById('counter');
  if (story && counter) {
    var max = parseInt(story.getAttribute('maxlength'), 10) || 10000;
    function tick(){
      var n = story.value.length;
      counter.textContent = n.toLocaleString() + ' of ' + max.toLocaleString() + ' characters';
      counter.classList.toggle('near', n > max * 0.9);
    }
    story.addEventListener('input', tick); tick();
  }
})();

/* ── The Verification Desk ────────────────────────────────────────────────
   Pure progressive enhancement. With this block deleted the page still
   works: evidence and curator findings are <details>, verdicts are radios.
   This adds the running tally and the finding sheet. Nothing is stored
   anywhere and nothing is sent anywhere. */
(function(){
  'use strict';
  var desk = document.querySelector('.claims');
  if (!desk) return;

  var claims = [].slice.call(document.querySelectorAll('.cl'));
  var doneEl = document.getElementById('done');
  var status = document.getElementById('status');
  var body   = document.getElementById('sheet-body');
  var note   = document.getElementById('copy-note');
  var LABEL  = {confirmed:'Confirmed', unsupported:'Not supported', contradicted:'Contradicted'};
  var agreeLine = null;

  function picked(cl){
    var r = cl.querySelector('.vd input[type=radio]:checked');
    return r ? r.value : null;
  }
  function citedBy(cl){
    var r = cl.querySelector('.cite input[type=radio]:checked');
    if (!r) return null;
    if (r.value === '0') return 'none of the evidence convinced me';
    var lab = r.closest('label');
    return 'evidence ' + r.value + ' — ' + lab.querySelector('span').textContent.replace(/^\d+\.\s*/,'');
  }

  /* Say, right under the evidence question, that the choice was recorded and where it went.
     (Raya's change from PR #4.) */
  function updateCiteNote(cl, verdict){
    var fs = cl.querySelector('.cite'); if (!fs) return;
    var note = fs.querySelector('.cite-note');
    var r = fs.querySelector('input[type=radio]:checked');
    if (!r){ if (note) note.remove(); return; }
    if (!note){ note = document.createElement('p'); note.className = 'cite-note'; note.setAttribute('aria-live', 'polite'); fs.appendChild(note); }
    var what = (r.value === '0') ? 'none of the evidence convinced you' : 'evidence ' + r.value + ' settled it';
    note.textContent = verdict ? 'Noted: ' + what + '. Added to your finding sheet below.'
      : 'Noted: ' + what + '. Record your finding above too, and this will be added to your finding sheet.';
  }

  function render(){
    var rows = [], done = 0, agree = 0;

    claims.forEach(function(cl){
      var v = picked(cl), truth = cl.dataset.verdict;
      var tag = cl.querySelector('.agree-note');
      updateCiteNote(cl, v);

      if (!v){
        delete cl.dataset.answered;
        if (tag) tag.remove();
        return;
      }
      done++;
      cl.dataset.answered = '1';

      var same = (v === truth);
      if (same) agree++;

      /* open the curator's finding the moment a verdict is recorded —
         this is the discovery beat, and it never closes again */
      var cur = cl.querySelector('.cur');
      if (cur && !cur.open) cur.open = true;

      if (!tag){
        tag = document.createElement('p');
        tag.className = 'agree-note';
        cur.parentNode.insertBefore(tag, cur.nextSibling);
      }
      tag.className = 'agree-note' + (same ? ' yes' : '');
      tag.textContent = same
        ? 'Your finding matches the curator.'
        : 'You said ' + LABEL[v] + '. The curator said ' + LABEL[truth] + '. Both are on the record.';

      rows.push({
        caseName: cl.dataset.case,
        n: cl.dataset.n,
        text: cl.querySelector('.cl-text').textContent.trim(),
        mine: LABEL[v],
        theirs: LABEL[truth],
        cite: citedBy(cl),
        same: same
      });
    });

    if (doneEl) doneEl.textContent = String(done);

    if (!agreeLine && status){
      agreeLine = document.createElement('span');
      agreeLine.className = 'agree';
      status.querySelector('p').appendChild(agreeLine);
    }
    if (agreeLine){
      agreeLine.textContent = done
        ? 'You and the curator agree on ' + agree + ' of ' + done + '. Disagreeing is allowed — the reasoning is shown either way.'
        : '';
    }

    if (!rows.length){
      body.innerHTML = '<p class="sheet-empty">No findings recorded yet. Start with any case file above.</p>';
      return;
    }

    var ol = document.createElement('ol');
    ol.className = 'sheet-list';
    rows.forEach(function(r){
      var li = document.createElement('li');
      var c  = document.createElement('span');
      c.className = 'sl-case';
      c.textContent = r.caseName + ' — claim ' + r.n;
      var t  = document.createElement('span');
      t.className = 'sl-claim';
      t.textContent = r.text;
      var v  = document.createElement('span');
      v.className = 'sl-v ' + (r.same ? 'match' : 'differ');
      v.textContent = r.same ? r.mine : r.mine + ' / curator: ' + r.theirs;
      li.appendChild(c); li.appendChild(t); li.appendChild(v);
      if (r.cite){
        var ci = document.createElement('span');
        ci.className = 'sl-cite';
        ci.textContent = 'Settled on ' + r.cite;
        li.appendChild(ci);
      }
      ol.appendChild(li);
    });
    body.innerHTML = '';
    body.appendChild(ol);
  }

  /* One listener on the document, matching BOTH the verdict radios (v-) and the
     citation radios (s-). The previous version bound to the first case file's
     parent section, so citations recorded in case files 2-5 were silently
     dropped from the finding sheet. */
  document.addEventListener('change', function(e){
    var t = e.target;
    if (t && t.type === 'radio' && /^[vs]-/.test(t.name || '')) render();
  });

  function say(msg){
    if (!note) return;
    note.hidden = false;
    note.textContent = msg;
  }

  var copyBtn = document.getElementById('copy-sheet');
  if (copyBtn) copyBtn.addEventListener('click', function(){
    var lines = ['Verification Desk — finding sheet',
                 'Immigrant Hall of Honor', ''];
    claims.forEach(function(cl){
      var v = picked(cl); if (!v) return;
      lines.push(cl.dataset.case + ' — claim ' + cl.dataset.n);
      lines.push('  Claim:    ' + cl.querySelector('.cl-text').textContent.trim());
      lines.push('  My finding:        ' + LABEL[v]);
      var ct = citedBy(cl);
      if (ct) lines.push('  Settled on:        ' + ct);
      lines.push("  Curator's finding: " + LABEL[cl.dataset.verdict]);
      lines.push('');
    });
    if (lines.length <= 3){ say('Nothing to copy yet — record a finding first.'); return; }
    var text = lines.join('\n');
    if (navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(
        function(){ say('Copied. Paste it wherever you keep notes.'); },
        function(){ say('Could not reach the clipboard. Select the sheet above and copy it by hand.'); });
    } else {
      say('This browser will not let a page use the clipboard. Select the sheet above and copy it by hand.');
    }
  });

  var printBtn = document.getElementById('print-sheet');
  if (printBtn) printBtn.addEventListener('click', function(){ window.print(); });

  var clearBtn = document.getElementById('clear-sheet');
  if (clearBtn) clearBtn.addEventListener('click', function(){
    claims.forEach(function(cl){
      [].slice.call(cl.querySelectorAll('input[type=radio]:checked'))
        .forEach(function(r){ r.checked = false; });
      var cur = cl.querySelector('.cur'); if (cur) cur.open = false;
    });
    render();
    say('Cleared. Every verdict is yours to change as often as you like.');
    var first = document.querySelector('.cl input[type=radio]');
    if (first) first.focus();
  });

  render();
})();


/* One-time gallery entrances. No hidden content, scroll interception, or requests. */
(function(){
  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motion.matches || !('IntersectionObserver' in window)) return;
  var items = document.querySelectorAll('.museum-home .hero-copy, .portrait-assembly, .museum-home > section:not(.arrival-hero), .museum-home .portrait-card');
  var observer = new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if (!entry.isIntersecting) return;
      entry.target.classList.add('exhibit-enter');
      observer.unobserve(entry.target);
    });
  }, {threshold:0.08});
  items.forEach(function(item){observer.observe(item);});
  motion.addEventListener('change', function(event){
    if (!event.matches) return;
    observer.disconnect();
    items.forEach(function(item){item.classList.remove('exhibit-enter');});
  });
})();


/* Exhibit scroll reveal. Section blocks on an inductee page ease in as the
   reader reaches them. Pure enhancement: the hidden start state lives behind
   html.reveal-on, which is added here only when motion is allowed, so with
   this file removed every block stays visible. The hero is left untouched,
   and blocks already on screen at load are revealed in the same synchronous
   pass — before the browser paints — so nothing flashes. */
(function(){
  'use strict';
  var profile = document.querySelector('.ihh-profile');
  if (!profile) return;
  if (!('IntersectionObserver' in window)) return;
  var motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (motion.matches) return;

  var targets = [].slice.call(profile.querySelectorAll(
    '.sec, .doc, blockquote.pull, .qs, .acts, .sources, .colophon'));
  if (!targets.length) return;

  targets.forEach(function(el){ el.classList.add('rv'); });
  document.documentElement.classList.add('reveal-on');

  /* Reveal anything already in (or above) the viewport immediately, in this
     same tick, so the first painted frame shows them fully — no flash. */
  var vh = window.innerHeight || document.documentElement.clientHeight;
  var pending = [];
  targets.forEach(function(el){
    var r = el.getBoundingClientRect();
    if (r.top < vh * 0.92) el.classList.add('is-in');
    else pending.push(el);
  });

  if (!pending.length) return;
  var observer = new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-in');
      observer.unobserve(entry.target);
    });
  }, {rootMargin:'0px 0px -12% 0px', threshold:0});
  pending.forEach(function(el){ observer.observe(el); });

  /* If the reader turns on reduced-motion mid-visit, drop the effect and
     make sure every block is shown. */
  motion.addEventListener('change', function(event){
    if (!event.matches) return;
    observer.disconnect();
    targets.forEach(function(el){ el.classList.add('is-in'); });
  });
})();

/* Interviews and media: a recording whose holder granted permission loads only when the visitor
   presses Play, so the page makes no request to the player's host until then. Without this
   script the Play button is an ordinary link to the holder's page. */
(function(){
  'use strict';
  [].slice.call(document.querySelectorAll('.ms-embed[data-embed]')).forEach(function(box){
    var play = box.querySelector('.ms-play'), src = box.getAttribute('data-embed');
    if (!play || !/^https:\/\//.test(src)) return;
    play.addEventListener('click', function(e){
      e.preventDefault();
      var f = document.createElement('iframe');
      f.src = src;
      f.title = box.getAttribute('data-title') || 'Recording';
      f.setAttribute('allow', 'fullscreen; picture-in-picture');
      f.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
      f.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-presentation allow-popups');
      f.className = 'ms-frame';
      box.textContent = '';
      box.appendChild(f);
      f.focus();
    });
  });
})();

/* ── Look closer: zoom ───────────────────────────────────────────────────
   The document image and its numbered notes work without this. The button
   only enlarges the image inside its own scrolling frame. */
(function(){
  'use strict';
  var btns = document.querySelectorAll('.lc-zoom');
  Array.prototype.forEach.call(btns, function(b){
    var stage = document.getElementById(b.getAttribute('aria-controls'));
    if (!stage) return;
    b.addEventListener('click', function(){
      var on = stage.classList.toggle('lc-zoomed');
      b.setAttribute('aria-pressed', String(on));
      if (on) {
        stage.setAttribute('tabindex', '0');
        stage.setAttribute('role', 'group');
        stage.setAttribute('aria-label', 'Zoomed document. Scroll or use the arrow keys to move around it.');
      } else {
        ['tabindex', 'role', 'aria-label'].forEach(function(a){ stage.removeAttribute(a); });
      }
    });
  });
})();
