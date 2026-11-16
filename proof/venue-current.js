(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.d3730193f1369c71.js","sha256":"d3730193f1369c71e2634c2262456dbd1a4397268466d1f8a6987f16e1a823a5","count":181});
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
