(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2110a2982de3acb6.js","sha256":"2110a2982de3acb6aa045fc23504ca6c73313fc86662e3e5de8668c08c342bb5","count":179});
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
