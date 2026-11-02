(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.17b124884271e0de.js","sha256":"17b124884271e0de165ef6390e6d80268c511bd485aaf0b2fb8f56a50c648166","count":152});
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
