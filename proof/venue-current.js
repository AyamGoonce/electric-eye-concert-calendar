(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.6fd3fe800ef7d9ac.js","sha256":"6fd3fe800ef7d9ac10910dd4c3e8f0a3dce6a8f5b9abb7d46154101c707c904d","count":179});
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
