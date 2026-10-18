(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.75b6b375cf98bca0.js","sha256":"75b6b375cf98bca0f1d3d50bb9df1f57ed683b1805147c13f421512bc255c157","count":154});
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
