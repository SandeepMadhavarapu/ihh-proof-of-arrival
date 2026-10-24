/* Visitor Voices: the LOCAL DEMO adapter. Copied only into voices/.demo/site by
   voices/demo_server.py and loaded before margin-notes.js there. It is never part of site/,
   and tests/test_voices.py checks that. It talks only to the demo server on this computer. */
(function(){
  'use strict';
  var A = window.IHHVoicesAdapters = window.IHHVoicesAdapters || {};
  A.demo = {
    send: function(p, cfg){
      return fetch(cfg.api + '/submit', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                         body: JSON.stringify(p), credentials: 'same-origin'})
        .then(function(r){ return r.json().then(function(j){ if (!r.ok) throw new Error(j.error || 'failed'); return j.message; }); });
    },
    load: function(cfg){
      return fetch(cfg.api + '/notes?page=' + encodeURIComponent(cfg.page), {credentials: 'same-origin'})
        .then(function(r){ return r.ok ? r.json() : {notes: []}; })
        .then(function(j){ return j.notes || []; });
    }
  };
})();
