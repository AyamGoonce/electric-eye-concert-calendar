(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.11371ddb4e91a2ea.js","sha256":"11371ddb4e91a2eaf9c3a60fd83ac1229514fa827bf3d1037882c23a13ad913c","count":154});
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
