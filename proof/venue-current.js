(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.02fea4280f6d1453.js","sha256":"02fea4280f6d1453a760f322bf30e7ec881bad5de7e39134dee0ea7ae73cfacb","count":169});
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
