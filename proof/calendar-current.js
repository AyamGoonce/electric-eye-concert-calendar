(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cee823185b82631b.js","sha256":"cee823185b82631bf31bb30018a7ae3a3c7c48d8ac5a24c95953f49fd3584bd2","count":1732});
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
