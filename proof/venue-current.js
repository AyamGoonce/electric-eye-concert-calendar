(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.81723e82d17f0d08.js","sha256":"81723e82d17f0d089cb7e9223d4568e40a59561faca1a20e2777de9b2f3cead9","count":176});
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
