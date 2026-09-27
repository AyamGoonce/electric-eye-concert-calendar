(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5ef4066f9c7ef579.js","sha256":"5ef4066f9c7ef5794b37829d5f0304769e30db0b102bb7d1617c0cafeb59760c","count":109});
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
