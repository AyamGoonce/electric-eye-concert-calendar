(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.208f02b27ea42d5d.js","sha256":"208f02b27ea42d5d272556f011f1b50225ee0f5d395ba536db9849327a6ce5d4","count":152});
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
