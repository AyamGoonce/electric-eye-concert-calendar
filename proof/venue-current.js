(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.77bb22081fc099ed.js","sha256":"77bb22081fc099edbd5790649f7701f4b8d0e07396f2cdae73733c6c48fe2fb6","count":169});
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
