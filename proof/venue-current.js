(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2ad821d7c8728c2a.js","sha256":"2ad821d7c8728c2abc7424d4f45593311d9d3bf00a32186c462aa578444a3ee1","count":109});
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
