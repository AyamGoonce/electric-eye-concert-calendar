(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8c7a33902ac91fb0.js","sha256":"8c7a33902ac91fb0af44f59aea8d2cb6ba8cd04b4310c8fb81071d43009256a5","count":1733});
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
