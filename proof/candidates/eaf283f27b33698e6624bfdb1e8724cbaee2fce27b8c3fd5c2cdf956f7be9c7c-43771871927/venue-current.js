(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.aeabc61bd840c0c8.js","sha256":"aeabc61bd840c0c82d98dbf701f5e842888406c37269733f84e98a3791352c28","count":179});
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
