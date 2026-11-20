(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a07b55442189f3e6.js","sha256":"a07b55442189f3e66c3d3808bc6e5c8efa8fd619f7baee589f4a56e43424d67b","count":182});
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
