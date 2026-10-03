(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b8f73de32b3a7ecb.js","sha256":"b8f73de32b3a7ecbbddb57689c3b5715882107a25e4b952ef7a23ced2671e428","count":169});
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
