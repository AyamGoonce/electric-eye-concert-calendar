(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ac7eed30a938014b.js","sha256":"ac7eed30a938014b1def01094ed0079b9951f5dbaaaf36ec12a0fa83c72d6638","count":166});
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
