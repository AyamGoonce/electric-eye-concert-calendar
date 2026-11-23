(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.70128b51abd006d6.js","sha256":"70128b51abd006d6c89a6e8c9b7b50c95d0529a2ff52f685ab7949de5a36f0c6","count":178});
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
