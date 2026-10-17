(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.44e664461a3edc46.js","sha256":"44e664461a3edc46a0b72b46eea68df1e1921f90603960516c56617e4a812637","count":157});
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
