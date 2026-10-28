(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.00cafd350c1a8548.js","sha256":"00cafd350c1a8548ca304e5dbb3a9c7af71b12d961c7b5c7e98da54d09d7176f","count":155});
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
