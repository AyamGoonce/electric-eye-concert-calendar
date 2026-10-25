(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5f538f160b26bfdd.js","sha256":"5f538f160b26bfdd766026d459459b72dfafe22c0db22e88fc651452b88f9b07","count":154});
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
