(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.6f8ef04289f1f9cc.js","sha256":"6f8ef04289f1f9cc92b43e16331358449408dc12ce1d30f7b761528f29cad6d4","count":166});
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
