(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0bf0f00311058a6f.js","sha256":"0bf0f00311058a6f10f87c98b059d861ff0c20445ec98780d65c5b173a20af7d","count":181});
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
