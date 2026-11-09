(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0c7a88bcfd40b073.js","sha256":"0c7a88bcfd40b073bc9b634a24df1c8959c12285af091adf78daaa5daf42c772","count":149});
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
