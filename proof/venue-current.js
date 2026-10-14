(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8fa44170533f6ed4.js","sha256":"8fa44170533f6ed46115a18536201526f793ff2a25f25237c0d4e964d9df66c0","count":164});
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
