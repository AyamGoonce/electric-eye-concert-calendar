(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b0ef4a9b3d1315df.js","sha256":"b0ef4a9b3d1315df905e45cd036fbf8dfcd10d390a07421283c6e32aad065d2e","count":152});
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
