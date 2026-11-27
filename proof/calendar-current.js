(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c6f388ec294c3224.js","sha256":"c6f388ec294c3224c9bfff2dc6cfbe9eccc31486de7db65c820266e6967a69c4","count":2106,"publishedAt":"2026-11-27T12:32:34Z","state":"calendar-state.json","stateSha256":"90727fc5903d1bdc2bd5ddb60a13c38ea65bf2d4e31b39936068f746bfd2ea2d","sourceState":"calendar-source-state.json","sourceStateSha256":"c894447147df22c53641a645c710ce127841a7af75f5794770b7a7c1eaf94307"});
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
