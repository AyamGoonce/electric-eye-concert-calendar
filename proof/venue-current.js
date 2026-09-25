(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.da5a7cd1989a6e39.js","sha256":"da5a7cd1989a6e3932cf894f6df7212487791e5878c0fa3c24d7b7ebae4c280e","count":109});
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
