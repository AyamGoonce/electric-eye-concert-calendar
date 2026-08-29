(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a42437e8ff0240fd.js","sha256":"a42437e8ff0240fdab7ea4635aa80084aa5a72ab60b2e62be1ef9d34b63050ce","count":2065,"publishedAt":"2026-08-29T09:38:12Z","state":"calendar-state.json","stateSha256":"d6ca3fa8be812913f9d5a171fb7c2a66b2910b52c1882e067dd1b76050a4b3dd"});
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
