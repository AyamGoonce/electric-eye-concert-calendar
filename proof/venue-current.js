(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b1de52b1b74d2832.js","sha256":"b1de52b1b74d2832a5750c982364b275c066a8852ac05608aab1b11e7f6f5b9d","count":179});
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
