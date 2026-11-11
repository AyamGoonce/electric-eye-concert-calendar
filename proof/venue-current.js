(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.06d2b9b1937e74a7.js","sha256":"06d2b9b1937e74a7a164f50fbf7a4aa929b0e04af85122a9688e82a952e2136f","count":176});
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
