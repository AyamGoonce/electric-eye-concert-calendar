(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7b5930f0ea3c3999.js","sha256":"7b5930f0ea3c3999c1389f891f395eb014f642193481c3ca47b565de6d4174bd","count":154});
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
