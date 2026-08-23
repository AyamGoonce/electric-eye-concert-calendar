(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1edd2626289d0a21.js","sha256":"1edd2626289d0a21d015482b1161bc5271e3650033e9bf34b153bf07ab15c4a8","count":1708});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
