(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0e61202456bbc50c.js","sha256":"0e61202456bbc50c326bbada2b306f182e6fabe4d80e792fc8ea6f7006975666","count":180});
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
