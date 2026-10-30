/* Visitor Voices: the PREVIEW adapter, for the public demonstration build only.
   Copied into the live build by tools/build_live.py and loaded before margin-notes.js there.
   It is never part of site/ or of the WordPress handover, and tests check that.

   Nothing a visitor writes leaves their browser: notes are kept in this browser's
   localStorage, and the curator preview page (curator-preview.html) in the SAME browser is the
   only place they can be approved. An approved note then appears beside its passage, for this
   browser only. Nothing is sent to the Immigrant Hall of Honor or to anyone else. */
(function(){
  'use strict';
  var KEY = 'ihh-preview-notes-v1';
  var TYPES = {perspective: 'My perspective', more: 'I know more', wrong: 'Something looks wrong', question: 'Question'};
  var EMAIL = /[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+/g;
  var IS_EMAIL = /[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+/;

  function read(){
    try { var v = JSON.parse(window.localStorage.getItem(KEY) || '[]'); return Array.isArray(v) ? v : []; }
    catch (e) { return []; }
  }
  function write(list){
    try { window.localStorage.setItem(KEY, JSON.stringify(list)); return true; }
    catch (e) { return false; }
  }
  function firstName(n){
    var w = String(n || '').trim().split(/\s+/)[0] || '';
    w = w.replace(/[^\w'\-]/g, '').slice(0, 20);
    return w && !IS_EMAIL.test(n) ? w : 'A visitor';
  }
  /* The same fields the production pipeline would show: never the email, never a source link. */
  function shown(i){
    var o = {id: i.id, kind: i.kind, page: i.page, anchor: i.anchor || '', selector: i.selector || {},
             type: i.type, type_label: i.kind === 'finding' ? 'My finding' : (TYPES[i.type] || 'Note'),
             text: String(i.text || '').replace(EMAIL, '[email removed]'), by: firstName(i.name), date: i.date};
    if (i.kind === 'finding') o.verdict = i.verdict || '';
    return o;
  }

  var A = window.IHHVoicesAdapters = window.IHHVoicesAdapters || {};
  A.preview = {
    send: function(p){
      var list = read();
      var item = {id: 'pv-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
                  status: 'pending', kind: p.kind, type: p.type, page: p.page, anchor: p.anchor || '',
                  selector: p.selector || {}, verdict: p.verdict || '', text: String(p.text || '').slice(0, 1000),
                  name: String(p.name || '').slice(0, 80), date: new Date().toISOString().slice(0, 10)};
      list.push(item);
      if (!write(list)) return Promise.reject(new Error('storage unavailable'));
      return Promise.resolve('Saved in this browser only — nothing was sent anywhere. In the museum, a curator ' +
                             'reads every note before it appears. To play the curator, open the curator preview ' +
                             '(link in the banner at the top of the page).');
    },
    load: function(cfg){
      return Promise.resolve(read().filter(function(i){
        return i.status === 'approved' && (i.kind === 'note' || i.kind === 'finding') && i.page === cfg.page;
      }).map(shown));
    },
    _all: read, _save: write, _shown: shown
  };
})();
