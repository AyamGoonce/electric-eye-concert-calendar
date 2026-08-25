(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.9c97fa9d91dcce91.js","sha256":"9c97fa9d91dcce914b6af6e9a3f8600ce6d9ddee0d9e1a8687f8a98a8960559d","count":1739,"publishedAt":"2026-08-25T14:14:36Z","state":"calendar-state.json","stateSha256":"9024d8bbba1402e4b302b2575b591af1953046964fe3050f34c0bd5c90e0d8de"});
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
