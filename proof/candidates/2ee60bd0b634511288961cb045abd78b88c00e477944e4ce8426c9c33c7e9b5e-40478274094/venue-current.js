(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.14b4bb78e9a60bf0.js","sha256":"14b4bb78e9a60bf0fdc70d607eb76528dde4bddf2720eb6589534d55e5a6e3dd","count":154});
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
