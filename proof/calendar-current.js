(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.79528788bed8d54d.js","sha256":"79528788bed8d54df7af3f63a7cfb767203260eafce2bc5f541cdc4e95739b8a","count":2220,"publishedAt":"2026-10-01T08:17:14Z","state":"calendar-state.json","stateSha256":"9afdb9f465de4010f44304d7ce557e646589fffe8245ba1cc1a5415aec08ce95","sourceState":"calendar-source-state.json","sourceStateSha256":"00e2e32f194210e2c6c8e5fd7aa108afbd164ee67453c87c5e4aadd4bcbb6f7c"});
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
