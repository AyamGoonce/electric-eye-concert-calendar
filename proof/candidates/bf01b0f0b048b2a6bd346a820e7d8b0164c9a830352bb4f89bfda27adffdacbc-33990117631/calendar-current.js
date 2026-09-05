(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bf01b0f0b048b2a6.js","sha256":"bf01b0f0b048b2a6bd346a820e7d8b0164c9a830352bb4f89bfda27adffdacbc","count":2522,"publishedAt":"2026-09-05T20:36:03Z","state":"calendar-state.json","stateSha256":"514b223f5061e18d730a64c354515a117de60b0428113dccbab7168e05c8a05b"});
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
