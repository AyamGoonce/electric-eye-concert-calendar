(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.d9f7919e8d4317d1.js","sha256":"d9f7919e8d4317d1729accea9f050bc9df6bdcf8b41e1e170044f6eb28491d96","count":109});
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
