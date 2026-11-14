(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.fd59d72023366a8c.js","sha256":"fd59d72023366a8c8a05bc248cd21ae2553cb6c985ada00842fbea12732b3d8c","count":180});
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
