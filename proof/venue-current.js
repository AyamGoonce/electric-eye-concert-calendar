(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a25cdae9514e4226.js","sha256":"a25cdae9514e42261d4aeabe6e1c74c9fc3901a71c8201415d2f6f82d6c96346","count":180});
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
