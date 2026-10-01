(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.60cb7c4a512437ce.js","sha256":"60cb7c4a512437ce1ff9d69fc287af6a3dd9e14455c253e23804d040bb365545","count":109});
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
