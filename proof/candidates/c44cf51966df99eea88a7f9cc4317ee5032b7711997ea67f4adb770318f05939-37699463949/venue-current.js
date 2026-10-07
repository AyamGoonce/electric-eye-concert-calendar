(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.cc5b4aa44ea4fd68.js","sha256":"cc5b4aa44ea4fd684378e35949a8f79a4bda3585bf20cfe53e33df7a43564047","count":167});
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
