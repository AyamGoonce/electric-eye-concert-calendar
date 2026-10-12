(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.438034b871ef8f2a.js","sha256":"438034b871ef8f2ae7d39b8e5d069c498863bc6e1209c7e8d4412f8cf7728622","count":165});
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
