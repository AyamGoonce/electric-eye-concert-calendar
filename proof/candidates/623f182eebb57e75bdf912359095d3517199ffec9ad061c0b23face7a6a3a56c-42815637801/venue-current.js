(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a6c9da79920f5383.js","sha256":"a6c9da79920f5383abb6c5e5bc0269b60373995bb39ed84a9a80b8d0478a7876","count":180});
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
