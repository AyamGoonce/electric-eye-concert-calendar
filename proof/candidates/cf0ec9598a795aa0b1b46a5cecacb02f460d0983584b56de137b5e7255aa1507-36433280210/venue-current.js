(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.32a4cbfda3676a0b.js","sha256":"32a4cbfda3676a0b3f2876e25148b404b657c56854407270850e41c60a58c97a","count":109});
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
