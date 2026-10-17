(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.954029d860cafb57.js","sha256":"954029d860cafb57d01c39020072ef5738d9ab5acb8e115e81bad4d786e309f0","count":157});
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
