(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.61cbf8baa2e736eb.js","sha256":"61cbf8baa2e736eb710bc42c34a0222c9f66493dee1d12cf7da090aa81563cf5","count":2480,"publishedAt":"2026-09-07T16:36:17Z","state":"calendar-state.json","stateSha256":"93590b4ff0b977e0463797d965df2d40dc7509f84ac077680a25baa10cdc6ca8"});
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
