(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.f47f3742cf85b38c.js","sha256":"f47f3742cf85b38c55ee50b36136478c0d6ae06f3aec2ef60367961b249d5c41","count":2091,"publishedAt":"2026-11-25T05:41:04Z","state":"calendar-state.json","stateSha256":"089d15da39dd82e1480d6d6e183aaecace812674e445490d17766f9ec645a75e","sourceState":"calendar-source-state.json","sourceStateSha256":"18f5c7a8811ca91ce6cd9c87b04bcb66bfee85db4447691478abe7f06d5accc4"});
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
