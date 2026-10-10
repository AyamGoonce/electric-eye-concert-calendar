(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.54b5cca3a3da30e8.js","sha256":"54b5cca3a3da30e89e546c3455814d81f02cb676e21ec9f77e9b91fb5bd16b64","count":166});
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
