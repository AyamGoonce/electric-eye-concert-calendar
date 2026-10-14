(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c883a6a0f96654ca.js","sha256":"c883a6a0f96654ca71f46aa834361e1750463a73870f7193b9a3469a25b5e8f3","count":2153,"publishedAt":"2026-10-14T08:48:59Z","state":"calendar-state.json","stateSha256":"27222c67725915211e47c2392359458705b698663e483a5f45d0199e0f0bccad","sourceState":"calendar-source-state.json","sourceStateSha256":"89624581509c4d844c03521c15ba1b77a2ba9946574b290294c2745704d95127"});
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
