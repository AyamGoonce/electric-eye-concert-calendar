(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.aa92c2b9f88db02d.js","sha256":"aa92c2b9f88db02dcef24a34017f2bc118e22e5bce2ffee544cca749069eb3b5","count":109});
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
