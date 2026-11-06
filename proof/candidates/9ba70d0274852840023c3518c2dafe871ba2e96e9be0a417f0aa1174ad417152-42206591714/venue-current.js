(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9a521d523e8f1bcf.js","sha256":"9a521d523e8f1bcf333d8a7a35369d40321ce75b046f0a6d57580282b30dd02a","count":150});
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
