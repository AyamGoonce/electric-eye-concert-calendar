(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.581d878ec2c355a9.js","sha256":"581d878ec2c355a969dbff5a9ce0d3228cb43f17ce7df9884f3f748565eeceb5","count":156});
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
