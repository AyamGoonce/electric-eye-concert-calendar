(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8257f5968f1f49f3.js","sha256":"8257f5968f1f49f3f0291cdc18d9152b627e636020f8338b805e1e82e7deca03","count":151});
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
