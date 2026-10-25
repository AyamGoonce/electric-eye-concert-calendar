(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.17f91c07d28de5aa.js","sha256":"17f91c07d28de5aa770a6f5957ae09df839c5cb06f7a636bd1ebe16733c92d1e","count":154});
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
