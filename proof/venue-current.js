(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2278c2b920536a9c.js","sha256":"2278c2b920536a9cdb91ca923daef73ee25fdd319afb77e8e42f459fb16cf4a9","count":177});
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
