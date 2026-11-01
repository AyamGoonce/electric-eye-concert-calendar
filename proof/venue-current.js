(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.4a2311a2f70ba733.js","sha256":"4a2311a2f70ba7331f76bb20e1c765f557042bb857c26c57e234202a641423b9","count":152});
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
