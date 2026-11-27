(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.669ca1b75d8e86d4.js","sha256":"669ca1b75d8e86d459592ac7921d31ff8fec63debc3ca87673ec7ee6008ab95d","count":181});
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
