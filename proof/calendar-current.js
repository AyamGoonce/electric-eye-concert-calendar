(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0f5d01d6a39e91fb.js","sha256":"0f5d01d6a39e91fbbc3be0f858c8441ee482e787d35d6454613898a0e255cb5a","count":2146,"publishedAt":"2026-11-20T11:50:08Z","state":"calendar-state.json","stateSha256":"60c3b268f1a4e6b1946d43e0a158547c735d71be0af5cd2415366d8dcd7cf86e","sourceState":"calendar-source-state.json","sourceStateSha256":"bdfe3df5e1f8a6f64c8783f8e2659d2d5fd4ba902339c8016396f7314613dca2"});
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
