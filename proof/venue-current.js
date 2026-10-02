(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7ae22e7ca8d506b1.js","sha256":"7ae22e7ca8d506b1167744fc0b2a7ccf98b482d21caafe35ef6a24f74690093c","count":109});
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
