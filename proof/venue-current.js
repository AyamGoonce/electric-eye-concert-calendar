(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0a17b2bd8d912a25.js","sha256":"0a17b2bd8d912a25903a326c1a3c43e8a24fc0e5f60d1d9354dd0cb5e6412725","count":165});
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
