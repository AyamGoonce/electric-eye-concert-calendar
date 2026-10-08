(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f7b9e6a5d06f2cd0.js","sha256":"f7b9e6a5d06f2cd0a7167ac5787969f11963d621484b50d87d9859d8dab684a1","count":168});
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
