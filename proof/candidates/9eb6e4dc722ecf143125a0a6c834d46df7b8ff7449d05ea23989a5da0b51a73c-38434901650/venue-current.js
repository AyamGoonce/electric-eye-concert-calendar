(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.e1a44554ce97ff69.js","sha256":"e1a44554ce97ff69dc4d50c8dd4c696a7d7b4de918d79b42b88b912473879175","count":164});
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
