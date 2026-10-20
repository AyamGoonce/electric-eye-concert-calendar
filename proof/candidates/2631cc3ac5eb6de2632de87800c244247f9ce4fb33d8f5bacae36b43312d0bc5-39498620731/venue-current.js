(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2c96b9a3bdd4b6cd.js","sha256":"2c96b9a3bdd4b6cd76a55a2d921e09ea9967b3f3d98170ab93637b471378fd66","count":156});
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
