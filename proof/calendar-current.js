(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.373522e00720ea66.js","sha256":"373522e00720ea66fbabb68e8f2d8207f714bdebb222fdd537fc876a15218f12","count":2157,"publishedAt":"2026-10-12T21:20:17Z","state":"calendar-state.json","stateSha256":"4f15d0c9b57d2ebad99536da3ccd916abf6c55bb1b5190471ceb7a03d15f5b1a","sourceState":"calendar-source-state.json","sourceStateSha256":"e398da80db5ed1cf2f47396abb21074ba4d1fa26782aef941d1874567bc2a630"});
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
