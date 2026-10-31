(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.d1ac8d3278de11cd.js","sha256":"d1ac8d3278de11cd17dc672e84d12c5bb640e93fb5550e30a2d3130a8249a36c","count":152});
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
