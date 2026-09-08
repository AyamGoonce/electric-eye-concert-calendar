(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a321da410d57b292.js","sha256":"a321da410d57b2929f6f8b537b5ec520a00e595e42c19df511c6d65c6032d4b1","count":2466,"publishedAt":"2026-09-08T04:54:14Z","state":"calendar-state.json","stateSha256":"01c652179d23d19826fe427b23a97075ee65edaf399e6a90a6c98c92ab95772a"});
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
