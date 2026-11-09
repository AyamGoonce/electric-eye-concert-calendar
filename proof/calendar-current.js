(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2fa5d86bd2fad038.js","sha256":"2fa5d86bd2fad03812235412b895430df9f869f0a36ed85ae0a2d50499c1c6e1","count":1971,"publishedAt":"2026-11-09T00:09:33Z","state":"calendar-state.json","stateSha256":"b8e5f423b6ed578384af2cbd157f50ce654d059d04ea6732fd135394c8cdfaed","sourceState":"calendar-source-state.json","sourceStateSha256":"70b1f0e4ff1e0566ba010c883daad0173641e08b031e2d6257361dbff39e8254"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
