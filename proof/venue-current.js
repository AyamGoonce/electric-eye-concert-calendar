(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.c737c21cc2931c50.js","sha256":"c737c21cc2931c50cdaafa4f34fde73b7f7c868d0fc5237ed9f536f4ed246f6f","count":152});
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
