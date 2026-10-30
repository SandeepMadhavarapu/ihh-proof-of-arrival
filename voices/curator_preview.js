/* Curator preview: lets the person using THIS browser play the museum's curator for the notes
   they wrote on the public demonstration build. Reads and writes only this browser's
   localStorage, through the preview adapter. Visitor text is shown with textContent only. */
(function(){
  'use strict';
  var A = (window.IHHVoicesAdapters || {}).preview;
  var box = document.getElementById('cp-queue');
  if (!A || !box) return;
  var KIND = {note: 'Margin note', claim: 'Report on a Verify claim', tip: 'Tip about an inductee', finding: 'Verify finding'};
  var PAGE = function(i){ return i.page === 'verify' ? 'verify.html' : (/^[a-z0-9-]+$/.test(i.page) ? i.page + '.html' : ''); };

  function el(tag, cls, text){ var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

  function render(){
    var list = A._all();
    box.textContent = '';
    if (!list.length){
      box.appendChild(el('p', 'cp-empty', 'Nothing here yet. Open any inductee profile or the Verify page, leave a note, and come back.'));
      return;
    }
    list.slice().reverse().forEach(function(i){
      var card = el('article', 'cp-item cp-' + i.status);
      var head = el('p', 'cp-meta');
      head.appendChild(el('span', 'cp-status', i.status.toUpperCase()));
      head.appendChild(document.createTextNode(' · ' + (KIND[i.kind] || 'Note') + ' · ' + (i.date || '')));
      card.appendChild(head);
      if (i.selector && i.selector.exact){
        var q = el('blockquote', 'cp-quote', i.selector.exact);
        card.appendChild(q);
      }
      card.appendChild(el('p', 'cp-text', i.text || '(no comment; a verdict only)'));
      var where = PAGE(i);
      if (where){
        var p = el('p', 'cp-where'), a = el('a', null, 'Open the page it belongs to');
        a.href = where + (i.anchor ? '#' + encodeURIComponent(i.anchor) : '');
        p.appendChild(a); card.appendChild(p);
      }
      var row = el('p', 'cp-actions');
      [['approved', 'Approve'], ['rejected', 'Reject'], ['delete', 'Delete']].forEach(function(b){
        var btn = el('button', 'btn small' + (b[0] === 'approved' ? '' : ' ghost'), b[1]);
        btn.type = 'button';
        btn.setAttribute('aria-label', b[1] + ': ' + (i.text || KIND[i.kind] || 'note').slice(0, 60));
        if (b[0] === i.status) btn.disabled = true;
        btn.addEventListener('click', function(){
          var all = A._all();
          all = b[0] === 'delete' ? all.filter(function(x){ return x.id !== i.id; })
                                  : all.map(function(x){ if (x.id === i.id) x.status = b[0]; return x; });
          A._save(all); render();
          var s = document.getElementById('cp-status'); if (s) s.textContent = b[1] + 'd.';
        });
        row.appendChild(btn);
      });
      card.appendChild(row);
      box.appendChild(card);
    });
  }
  render();
})();
