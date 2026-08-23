(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.198b600b5fb9f6c6.js","sha256":"198b600b5fb9f6c6d31c018b7d87585df4f0af42242ef92f053b90aef666eca7","count":1780});
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
