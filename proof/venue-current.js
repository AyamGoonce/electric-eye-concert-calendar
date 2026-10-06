(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a41a4276739215c2.js","sha256":"a41a4276739215c2d9d818eff390c7adb179a7c37cb3ab11f195c2c2291d7c54","count":168});
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
