(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0d70ea93b9983ac4.js","sha256":"0d70ea93b9983ac49556e547869bfa9f6978085621e1a1390b2a4ccdbc1be345","count":168});
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
