(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8520d0214b8da180.js","sha256":"8520d0214b8da1808c284be10f1ee3f411f7ba575c4cf44dc93f5131b541ae10","count":2122,"publishedAt":"2026-11-17T16:09:21Z","state":"calendar-state.json","stateSha256":"199a3bb3a5bf53f92a0e4b393d6db95e390a6ab20ce838e8874eb618963efe22","sourceState":"calendar-source-state.json","sourceStateSha256":"e5cf140e19a3a90e11e8175fe1299b74d85db613af88972155bbc6aefa465ab8"});
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
