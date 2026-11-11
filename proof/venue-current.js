(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.c32a47e2c254cbff.js","sha256":"c32a47e2c254cbff6a6aa5471baf584420e5c08bfb521744e2dcf6d47e174b8d","count":176});
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
