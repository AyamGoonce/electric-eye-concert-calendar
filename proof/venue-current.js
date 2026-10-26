(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a2aa9c6ec74ff40b.js","sha256":"a2aa9c6ec74ff40b068540fdf47c401cbe4ca8b2f06745f25fbd5d1f2544b4cd","count":154});
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
