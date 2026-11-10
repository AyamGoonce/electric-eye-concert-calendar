(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7f0e738a0bb3c2a2.js","sha256":"7f0e738a0bb3c2a2ca36fd7b28f852c18593ec137de19936a74edf189e727b9e","count":180});
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
