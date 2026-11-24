(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.b5e330eb983af94c.js","sha256":"b5e330eb983af94c42a98a758e17de248d74bf9a5f7ae0620abf15d99345b964","count":180});
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
