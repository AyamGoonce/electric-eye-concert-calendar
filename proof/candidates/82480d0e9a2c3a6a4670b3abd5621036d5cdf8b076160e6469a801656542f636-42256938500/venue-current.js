(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.d899df090dabdd2a.js","sha256":"d899df090dabdd2aded1bd928f7e5e107ebc59035579d1e0bc8444bd56a8e633","count":150});
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
