(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.c1d59bae02710c89.js","sha256":"c1d59bae02710c89649cea19be1df651635454fe5d6a20940a021052e7b854f1","count":159});
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
