(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.91998843389e32fe.js","sha256":"91998843389e32fefbf10bb0d14d96f0dd9e1b8c17b0e5f7511ac4bf7dc71ccd","count":1842,"publishedAt":"2026-08-26T20:11:08Z","state":"calendar-state.json","stateSha256":"126c2459d8ac3b18e2c3e4d5371fd8d02d9241563b9a45198e0e500213d56ba1"});
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
