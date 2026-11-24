(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7251fc0af826f201.js","sha256":"7251fc0af826f2010845251cba315f200d6377e9297e7aaf57ccbd0dbac39d2f","count":180});
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
