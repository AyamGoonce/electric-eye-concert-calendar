(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7d6968f7c507730f.js","sha256":"7d6968f7c507730f7b1f99ec1e722274db5b3a42ad2371e743ad3a00a847acc8","count":109});
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
