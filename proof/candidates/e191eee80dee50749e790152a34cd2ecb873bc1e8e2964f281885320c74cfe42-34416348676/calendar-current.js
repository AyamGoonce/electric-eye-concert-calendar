(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e191eee80dee5074.js","sha256":"e191eee80dee50749e790152a34cd2ecb873bc1e8e2964f281885320c74cfe42","count":2526,"publishedAt":"2026-09-09T23:21:57Z","state":"calendar-state.json","stateSha256":"743db2d52a8205cea148a8463c63ad41a30d298d62c758c5f11b29e33faeafe8"});
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
