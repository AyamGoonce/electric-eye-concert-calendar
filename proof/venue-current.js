(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.20ef4ae2a22d4e93.js","sha256":"20ef4ae2a22d4e932409586cc2be6d191f9e3d41adeb8c37ee422fc7b0560cb3","count":154});
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
