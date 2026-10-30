(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.4d5fca7d84540981.js","sha256":"4d5fca7d845409819809ef398b07db09a96e9d2f3368d8184eb62180227e9b85","count":149});
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
