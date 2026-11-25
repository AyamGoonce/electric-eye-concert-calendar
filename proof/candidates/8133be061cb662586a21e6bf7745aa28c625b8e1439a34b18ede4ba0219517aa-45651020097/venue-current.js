(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8a30fe9e6c676483.js","sha256":"8a30fe9e6c6764836bf349fc9cd20958b72360520215fc7331825d0d21fc989a","count":182});
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
