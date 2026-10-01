(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.69edee0805651bbd.js","sha256":"69edee0805651bbd23d61bbd2bf014be33c371b7d05d649a9b66afddbfc089bf","count":109});
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
