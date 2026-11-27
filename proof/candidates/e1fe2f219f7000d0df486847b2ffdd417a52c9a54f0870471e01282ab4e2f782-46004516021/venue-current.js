(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f0144094b4084e88.js","sha256":"f0144094b4084e889d1d0560663e3f644acc4c64d9cb552bef3a9436283fe3a2","count":180});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeVenueManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:venue-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:venue-data-error", {detail:{reason:"venue data unavailable"}}));
  };
  document.head.appendChild(script);
}());
