(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9b6aad04c00f3d7a.js","sha256":"9b6aad04c00f3d7abe5e497b5bf7c9015d0151f9da878a0a9f46556e2691bb09","count":155});
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
