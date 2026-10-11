(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.dd9d43000292439a.js","sha256":"dd9d43000292439a46a8f21c7fb948e4c54086cb0c42d7cb4c80b3b6cb118662","count":166});
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
