(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.1e3c8d1748ebbd20.js","sha256":"1e3c8d1748ebbd209b4143b4ca2e8a1a46ee7a1ac436ad1a5a349d1a836b3656","count":155});
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
