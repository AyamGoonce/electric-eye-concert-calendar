(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cd51d65afb95c0a3.js","sha256":"cd51d65afb95c0a31f0b83c6b65c2b1b7021c0042be59c4ef07718f500d72b1e","count":2066,"publishedAt":"2026-08-29T13:34:01Z","state":"calendar-state.json","stateSha256":"7ba1f18ffd19b89a41472a5ff24957e817db8f11735bbb3d25888f2923b8aba1"});
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
