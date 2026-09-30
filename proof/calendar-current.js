(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7291e0cde5aac9a9.js","sha256":"7291e0cde5aac9a9b439a7e5689a949fda504c9920c943f959a056e22c67493b","count":2232,"publishedAt":"2026-09-30T19:34:11Z","state":"calendar-state.json","stateSha256":"88fe3a9164f137dedcbcfe6ef6f0e196de874bdcd16f775daa0e6bd6ff10b0a9","sourceState":"calendar-source-state.json","sourceStateSha256":"bc529fba69648a827b04e5a7b63d444dd09e8950f6bbeb7ef318aa49ac1a9c37"});
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
