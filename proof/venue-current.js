(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.14eed6dfac1001d0.js","sha256":"14eed6dfac1001d076ddb07f798778f3a47a4cb41f6fb9fe07995f6aca9d56db","count":151});
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
