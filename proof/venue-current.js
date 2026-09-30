(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f702e9e39a3774a5.js","sha256":"f702e9e39a3774a5d35fdcd0e7e9061aa570f78848f527bc187b3030083bb37a","count":109});
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
