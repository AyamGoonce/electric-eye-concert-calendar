(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7d5cad6c9fc70e94.js","sha256":"7d5cad6c9fc70e94f7902ecdd25b0e770fbfe7a8918dc8b85518a54a02dafa2a","count":181});
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
