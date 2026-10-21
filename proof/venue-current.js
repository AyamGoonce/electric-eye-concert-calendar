(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2c7c0c01045b8dee.js","sha256":"2c7c0c01045b8deecbcab9ed315157e181d186f258b05dde3c1bc85592d0abcd","count":155});
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
