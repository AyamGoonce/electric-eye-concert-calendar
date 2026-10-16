(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.6cd7a768a33935cd.js","sha256":"6cd7a768a33935cd4ead509ab3c60a93a3cd5bf85340256f3599d81a61008e67","count":159});
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
