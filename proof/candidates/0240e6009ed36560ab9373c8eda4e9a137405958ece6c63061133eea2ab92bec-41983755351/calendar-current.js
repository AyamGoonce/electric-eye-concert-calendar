(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0240e6009ed36560.js","sha256":"0240e6009ed36560ab9373c8eda4e9a137405958ece6c63061133eea2ab92bec","count":2027,"publishedAt":"2026-11-05T06:58:17Z","state":"calendar-state.json","stateSha256":"72ea83136f14769006b7d7cb391e4e63bf5aa81a406bb6224662f3c854a31e5c","sourceState":"calendar-source-state.json","sourceStateSha256":"90296d1b21bdc99d8eb8da0173a28875d4add7e0477b18e41f1a183668885187"});
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
