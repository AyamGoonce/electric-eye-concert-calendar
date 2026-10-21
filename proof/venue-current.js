(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.4673b7e70fa32b2f.js","sha256":"4673b7e70fa32b2f9ebe1517a44b64b514fcd4958dc58939bd1d1f52077c759a","count":155});
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
