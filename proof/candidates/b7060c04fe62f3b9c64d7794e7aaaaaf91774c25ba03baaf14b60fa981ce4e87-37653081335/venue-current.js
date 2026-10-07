(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2f948922dbfc1361.js","sha256":"2f948922dbfc13618889c4ddb32c0f528e86f1ab2a35eeaa08505870d88e8262","count":167});
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
