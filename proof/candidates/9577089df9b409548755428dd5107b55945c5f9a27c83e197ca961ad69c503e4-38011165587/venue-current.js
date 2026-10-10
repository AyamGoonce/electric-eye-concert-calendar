(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8939a6e2108209a1.js","sha256":"8939a6e2108209a1c642ead524f25abda2053b72b11d13e877a3fafd0709215b","count":166});
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
