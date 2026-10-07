(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1b9b907b0fe0a490.js","sha256":"1b9b907b0fe0a4908cdf4c7fb1db05c6aecf523899904373766a1c6a190ad64b","count":167});
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
