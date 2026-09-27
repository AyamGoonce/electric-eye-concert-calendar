(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2c25765de4662fea.js","sha256":"2c25765de4662feaf30a1c1d9ce3037b6a77e7c991ebc938b570a8762ef9c4f2","count":109});
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
