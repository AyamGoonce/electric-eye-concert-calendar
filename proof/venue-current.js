(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0dae25dbb4cc3483.js","sha256":"0dae25dbb4cc3483720e344d2758e36522e64deebe85b21be6d39d125f7e5fa3","count":109});
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
