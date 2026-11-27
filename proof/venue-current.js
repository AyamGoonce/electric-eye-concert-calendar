(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.631b24bf1eb5104b.js","sha256":"631b24bf1eb5104b1df13ede7a64147f1b676fd3ea28cc2c822badd678cc8930","count":181});
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
