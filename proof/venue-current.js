(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9bb4d45e8c328d71.js","sha256":"9bb4d45e8c328d71538f94e3d31a3cd165b959036e8b073799672e376acc7efb","count":156});
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
