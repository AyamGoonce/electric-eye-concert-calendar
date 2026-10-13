(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.3d0d17eeef5e7e21.js","sha256":"3d0d17eeef5e7e212c0249a0f7cd9f6b819f52c92b173d68a70a73a235f656ff","count":164});
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
