(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.e225816d170efca0.js","sha256":"e225816d170efca03a2951a8f3cef570935eeadf1b8117831a1022788da196d9","count":178});
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
