(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a9cb7f160043c27e.js","sha256":"a9cb7f160043c27e35fe6c11cc46b37d73dac960b0c796b77bba5d64a3280091","count":179});
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
