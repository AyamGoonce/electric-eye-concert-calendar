(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.88a2def55e1ed6d8.js","sha256":"88a2def55e1ed6d872b6c7c8dc468dd69ec00b50ee144c1ba4320c1a7d46bb07","count":109});
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
