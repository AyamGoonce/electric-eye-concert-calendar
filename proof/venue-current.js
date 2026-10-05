(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5220b0d88bca48d5.js","sha256":"5220b0d88bca48d57b3694fb50e5ec66359bf49f1d45b2187626f7be546739ae","count":168});
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
