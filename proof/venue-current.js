(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7223594a2a9e5ac5.js","sha256":"7223594a2a9e5ac505abd76706493d912f1e4a438d6cf3a78c0bc5f0d186c314","count":156});
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
