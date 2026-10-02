(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.cb399df227ad29f0.js","sha256":"cb399df227ad29f04e07ebd6b340f0872261aec0fa596f327503eabd5caba6b0","count":169});
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
