(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.399295fe1c01ec5a.js","sha256":"399295fe1c01ec5a2ac3207947239fc768af055fa1727a5d10c5e6230da63e2d","count":181});
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
