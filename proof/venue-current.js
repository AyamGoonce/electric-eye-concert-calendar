(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.89e9f0480c018431.js","sha256":"89e9f0480c0184317d06d697ab90f2d98072943cec3d1ac8814bebf6e7a576d2","count":109});
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
