(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.e36a35e97d95ae3f.js","sha256":"e36a35e97d95ae3f303a4bffafbb469a2a4c1429f62fb947150f3fa9a66d30ae","count":176});
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
