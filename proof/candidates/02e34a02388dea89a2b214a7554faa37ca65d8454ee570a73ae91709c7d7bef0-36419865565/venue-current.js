(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.e148f0b8bf1760b9.js","sha256":"e148f0b8bf1760b92323be2aebe5c3d6de971896d5db02f3f66b3b3550f4fdaf","count":109});
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
