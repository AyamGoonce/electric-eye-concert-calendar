(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b26d7252bed1da92.js","sha256":"b26d7252bed1da92e7fcc407756ce8032156674178f1e9e9acffb3272024e3f2","count":156});
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
