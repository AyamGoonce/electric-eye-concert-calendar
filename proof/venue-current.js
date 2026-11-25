(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.31fab9bcf3f3f241.js","sha256":"31fab9bcf3f3f241c78a1986b68f06b2d90e5caeb49712dfac7639237bf292d4","count":179});
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
