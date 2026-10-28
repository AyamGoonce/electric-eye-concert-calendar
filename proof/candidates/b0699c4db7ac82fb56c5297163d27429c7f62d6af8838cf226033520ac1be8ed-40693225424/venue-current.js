(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7371687f649fa8e7.js","sha256":"7371687f649fa8e7a59ae3439fb112545085d51fc584edf2ae70645e34f44f98","count":155});
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
