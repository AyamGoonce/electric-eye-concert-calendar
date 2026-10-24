(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.3b05d959113e4e5a.js","sha256":"3b05d959113e4e5a9d4999c2d960a24bda5d3edc186879b5c7a89492ee06b02b","count":155});
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
