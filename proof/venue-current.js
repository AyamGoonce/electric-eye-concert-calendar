(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2d1fdd271166e1a4.js","sha256":"2d1fdd271166e1a4ccabf66c5f16f8db9560bda4d8c21226a31a549f37c28afa","count":168});
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
