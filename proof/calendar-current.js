(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.40307d97b174f376.js","sha256":"40307d97b174f37653f3b0efe0782a83410085e679294a2079561fb002d8f372","count":1740,"publishedAt":"2026-08-26T09:11:39Z","state":"calendar-state.json","stateSha256":"d00dbf1a43534a214720bfce2b06ad4130558b1f476dfd216b2ff33484fa0883"});
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
