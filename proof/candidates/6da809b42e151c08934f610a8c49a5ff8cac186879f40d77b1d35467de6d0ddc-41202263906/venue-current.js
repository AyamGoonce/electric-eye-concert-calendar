(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.61bfde1a43dc9e5c.js","sha256":"61bfde1a43dc9e5cbc564464abfa40a6ed7c9c5498af89ac314b0676ea681ae8","count":152});
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
