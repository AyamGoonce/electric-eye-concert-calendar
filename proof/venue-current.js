(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8d5d52542bf4f3dc.js","sha256":"8d5d52542bf4f3dce508119dd45d89403ce6d1ff3ee7a5d42ba336c2fbaecf31","count":154});
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
