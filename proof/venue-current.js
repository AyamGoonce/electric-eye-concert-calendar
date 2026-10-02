(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.3b21f863416a6dbc.js","sha256":"3b21f863416a6dbcdc1297b1f58065d58d9533251798e9eece7bac8428202c27","count":109});
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
