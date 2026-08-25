(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.5bc48c46fa52572a.js","sha256":"5bc48c46fa52572a791d5edd8971a74b90f24fd6c092f13ceaf3541383b14e89","count":1743,"publishedAt":"2026-08-25T19:05:30Z","state":"calendar-state.json","stateSha256":"1f66f0e3d8edce2ac293e9863a01d075370d4f9d5a4ab7d3bc984f60cf6550a3"});
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
