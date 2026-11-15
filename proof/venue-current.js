(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.efad0b1e36868001.js","sha256":"efad0b1e36868001e68655d5403052df729ff7c4764993c8bc60b34f4c9c5fac","count":180});
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
