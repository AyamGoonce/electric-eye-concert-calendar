(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2b92a3a2e7d82351.js","sha256":"2b92a3a2e7d8235108d606ce6b491b067108d97fe5691ffa00d2602198722f65","count":180});
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
