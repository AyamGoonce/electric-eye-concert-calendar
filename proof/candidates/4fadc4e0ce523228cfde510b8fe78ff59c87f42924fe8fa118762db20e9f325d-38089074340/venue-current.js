(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.839ec2a08ec3ffac.js","sha256":"839ec2a08ec3ffacd745d0eb0180b0f8a8347e568afb89894644dd36718923d2","count":165});
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
