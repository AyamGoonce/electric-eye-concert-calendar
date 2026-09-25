(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.515dd9acd948a23b.js","sha256":"515dd9acd948a23be515b3cf5da098839ddf2db1c996a8c4a7995dc51761c2e3","count":109});
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
