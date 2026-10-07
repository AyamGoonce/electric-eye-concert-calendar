(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.02554e54fcff94b5.js","sha256":"02554e54fcff94b5590c6a849b088505ed18aadca42cc49131f4f32b390cea2a","count":167});
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
