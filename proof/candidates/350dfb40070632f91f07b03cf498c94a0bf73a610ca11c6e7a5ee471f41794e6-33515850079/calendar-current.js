(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.350dfb40070632f9.js","sha256":"350dfb40070632f91f07b03cf498c94a0bf73a610ca11c6e7a5ee471f41794e6","count":2263,"publishedAt":"2026-09-01T13:58:38Z","state":"calendar-state.json","stateSha256":"3b9b7c8638bbee5d246a3d4e9af26e83291304a638c2e4a6b96fffd5721f6ac6"});
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
