(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.78b19b221328eb41.js","sha256":"78b19b221328eb41dfa459f59b212623ee287b558c27339188df892a7267e4c8","count":168});
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
