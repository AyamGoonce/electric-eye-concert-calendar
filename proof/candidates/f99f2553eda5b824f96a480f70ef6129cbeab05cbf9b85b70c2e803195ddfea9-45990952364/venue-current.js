(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.4495ed5e30aa68a7.js","sha256":"4495ed5e30aa68a7c0c70fb96c67459f03fd553aeae18a884e3bc5a690cf628d","count":180});
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
