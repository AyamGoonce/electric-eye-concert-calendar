(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.fdd58df70ac00596.js","sha256":"fdd58df70ac005961bcce192de1c6578b86db3c9d26e00f251586c7d678d8f7b","count":168});
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
