(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2c9e76eb90bab1ad.js","sha256":"2c9e76eb90bab1ad63651411344a3e996e4c99ff7b96de4439135ba211a49b09","count":152});
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
