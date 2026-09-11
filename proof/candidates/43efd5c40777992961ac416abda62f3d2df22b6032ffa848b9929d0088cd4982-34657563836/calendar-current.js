(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.43efd5c407779929.js","sha256":"43efd5c40777992961ac416abda62f3d2df22b6032ffa848b9929d0088cd4982","count":2488,"publishedAt":"2026-09-11T23:22:33Z","state":"calendar-state.json","stateSha256":"97406358d8bbb70938c1c3a868364f716fb4d6373985f81d9f4428d2eb22ad9e"});
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
