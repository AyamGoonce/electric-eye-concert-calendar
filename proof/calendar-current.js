(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8709b1665a0aed77.js","sha256":"8709b1665a0aed77c9c398f673446535f4cf8abe9df56f260dddf442a299f165","count":2124,"publishedAt":"2026-11-26T17:00:10Z","state":"calendar-state.json","stateSha256":"b9a6237d43f1e3c2095a7b4be260e72bc58a1d1dbe13374e31e0d38e7cddf805","sourceState":"calendar-source-state.json","sourceStateSha256":"0e66e18dea0e5831ddbe6865183fff1d59bfd19ca66204e2365ce9e653a60182"});
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
