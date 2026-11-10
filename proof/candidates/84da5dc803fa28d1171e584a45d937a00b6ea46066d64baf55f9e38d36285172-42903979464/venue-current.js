(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.dc64b2967f2e2394.js","sha256":"dc64b2967f2e239468ac574d164f27f55ce27ff035ae6235fb8ac084f44db700","count":180});
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
