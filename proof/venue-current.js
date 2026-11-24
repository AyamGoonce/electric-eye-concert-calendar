(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5573dbe4c4896b93.js","sha256":"5573dbe4c4896b93a579918c00ee3068e9d16423487ccb119d1f79ed980ba8d5","count":180});
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
