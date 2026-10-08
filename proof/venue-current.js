(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.d400a62415302ed0.js","sha256":"d400a62415302ed028f0d8edfc53d7e91a90e18f7f4b14c28bd1b1ec4bc8e151","count":168});
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
