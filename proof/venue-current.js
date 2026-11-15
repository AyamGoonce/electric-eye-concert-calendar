(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.802c3471ec38e561.js","sha256":"802c3471ec38e561a8b9fa860226dc05c44e35ebb5cc47c93c32b949df18aa54","count":179});
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
