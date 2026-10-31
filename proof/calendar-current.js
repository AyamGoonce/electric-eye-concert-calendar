(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.765c551a53006482.js","sha256":"765c551a53006482ee5dbb308788f1634a8cf061124741e867ec5401e627dbb5","count":2054,"publishedAt":"2026-10-31T11:46:58Z","state":"calendar-state.json","stateSha256":"89be67b121f83ec751c40834d82aeb4cebbc9f683ecea6a518cc6cdc6e3b12f4","sourceState":"calendar-source-state.json","sourceStateSha256":"5ba289f3fa618eca3e101c1a10f93448e24591abc5bad6d1eee6b30a54827880"});
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
