(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a189f7f50cfe0cc3.js","sha256":"a189f7f50cfe0cc3a03ed361026f38c98141c3c9df482d4543edb1033f87b120","count":165});
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
