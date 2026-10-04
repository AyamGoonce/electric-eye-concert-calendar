(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f952b55ebb3a817d.js","sha256":"f952b55ebb3a817dcb5937d1f9b6f07ee037fbc79cd200d603e97502071ee55b","count":168});
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
