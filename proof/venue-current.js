(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5403cc7f06b561f3.js","sha256":"5403cc7f06b561f36bd2063228221f4a441758f28de3f714d3ff574d51c00dbe","count":109});
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
