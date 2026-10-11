(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b9a58df9dfb7be9b.js","sha256":"b9a58df9dfb7be9bd8a6a62a93482531f5733aadcc02978efcfa6dd8d8650bf7","count":2169,"publishedAt":"2026-10-11T05:57:58Z","state":"calendar-state.json","stateSha256":"2294fce7a3e74dfaf2eb017e0028c25f58359f6dc95aa5ac0165900326c40649","sourceState":"calendar-source-state.json","sourceStateSha256":"03ec98a27982248edaf9767ad456c3de147181f2f1c741ba27971b88ba78061d"});
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
