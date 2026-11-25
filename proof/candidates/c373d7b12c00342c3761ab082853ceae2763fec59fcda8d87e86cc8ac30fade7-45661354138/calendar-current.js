(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c373d7b12c00342c.js","sha256":"c373d7b12c00342c3761ab082853ceae2763fec59fcda8d87e86cc8ac30fade7","count":2122,"publishedAt":"2026-11-25T17:09:56Z","state":"calendar-state.json","stateSha256":"68dacdb4579ecbdf78a82d8be36a71b5ac10256bc8f42995b3f4a196edae2559","sourceState":"calendar-source-state.json","sourceStateSha256":"d910ef6d172d1b71d49419db6430f42cfd475412857d4662ff7917eafeb4038e"});
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
