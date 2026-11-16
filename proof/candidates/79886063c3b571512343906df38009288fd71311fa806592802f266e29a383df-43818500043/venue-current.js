(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8e3f361b9e6dd506.js","sha256":"8e3f361b9e6dd5065c5e74ce6815d6f2693499b4b71dac7cd3d02518b8e0d458","count":179});
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
