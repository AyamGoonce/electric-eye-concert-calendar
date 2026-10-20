(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.97c47c2c6eefc094.js","sha256":"97c47c2c6eefc094122289657762a4cd95ea65cb1c3a27fcf4c032d8e2704904","count":156});
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
