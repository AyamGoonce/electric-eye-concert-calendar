(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.e429aaa64c54080a.js","sha256":"e429aaa64c54080ad4c0de76c0391facb483022cb6a58c9f13e5660d27b3672c","count":167});
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
