(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ed24f2c09382575d.js","sha256":"ed24f2c09382575d03ba9862bd8e761e454a16f9239d78a622b9aa895c7eaf1e","count":179});
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
