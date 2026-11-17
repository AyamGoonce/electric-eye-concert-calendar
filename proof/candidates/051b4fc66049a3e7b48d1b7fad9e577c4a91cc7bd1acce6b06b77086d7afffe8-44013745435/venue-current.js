(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7f8514482f540e8f.js","sha256":"7f8514482f540e8f38349ea9ed7a6163c6758ac97f9f831d13c6128a2cf94ff9","count":181});
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
