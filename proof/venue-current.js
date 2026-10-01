(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.bdbac10d2a691acc.js","sha256":"bdbac10d2a691acce119558e7e07e05f4d01b4cc55f9c0a734a1e55433fbc814","count":109});
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
