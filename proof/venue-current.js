(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.22b674c6c24e7aca.js","sha256":"22b674c6c24e7aca92058a3b1ca4eaf01c82e40f20d25bf340f1a8484aacb24e","count":180});
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
