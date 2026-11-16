(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1a4254f384270e88.js","sha256":"1a4254f384270e887e6810d44f8a676634991d5523159ba67c12fd87cf17bdbb","count":179});
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
