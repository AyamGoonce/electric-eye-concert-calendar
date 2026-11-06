(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.aedc048b7538aa70.js","sha256":"aedc048b7538aa70c4ed620880a86874a2393e52bf83912881e28fc7c12baec2","count":2020,"publishedAt":"2026-11-06T06:58:19Z","state":"calendar-state.json","stateSha256":"120e0011bd99fa0cf871c886abea0c5a8d0a6486d9f0ded9e17a24aba22166c9","sourceState":"calendar-source-state.json","sourceStateSha256":"2d0aa06735728d84df4a7c5a9497ff53448a38d9068f397f16a03113a16c84bf"});
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
