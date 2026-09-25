(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.08104054dbe13185.js","sha256":"08104054dbe13185c9a1bf7ae205ca0cd0af16e08d7ac0f3a8f35326f1632a4c","count":109});
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
