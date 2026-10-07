(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.162e9751aec5eb1c.js","sha256":"162e9751aec5eb1cc31c28ba431e85979e0d7e069ce9930237c96ba1d4629c00","count":167});
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
