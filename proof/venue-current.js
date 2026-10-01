(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.c7b828c4ec039ddc.js","sha256":"c7b828c4ec039ddc45058aac4532078396f21b05ff15dee095aa0f65573605d8","count":109});
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
