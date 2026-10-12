(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.7e667b9a5e792b2c.js","sha256":"7e667b9a5e792b2c1943d23cbd6885bc5f24e75109a30e03adcb5c05c7ee82c9","count":165});
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
