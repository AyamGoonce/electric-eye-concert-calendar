(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.11d71331d195b39d.js","sha256":"11d71331d195b39d5878c8c4d53b686d334cf9d47a3b4d21ab7421afbac23f67","count":181});
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
