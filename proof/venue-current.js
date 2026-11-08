(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.22cbdd467062b763.js","sha256":"22cbdd467062b763d6695eb6753ba97298a68cc8d6bd1e8ec6b3ddd3babe7d64","count":149});
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
