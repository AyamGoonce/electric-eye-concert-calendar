(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.73ccb8201b484296.js","sha256":"73ccb8201b4842960faa8e5b6e68cb068cab8f53863c2d41f1d595a0a8645bc9","count":179});
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
