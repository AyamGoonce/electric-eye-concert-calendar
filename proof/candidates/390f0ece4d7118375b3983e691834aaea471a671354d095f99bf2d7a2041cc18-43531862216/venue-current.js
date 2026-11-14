(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.c57c41961959adb1.js","sha256":"c57c41961959adb13e118c5d6d061cf173fb7072d6089ce07807e9ac7526dbe9","count":179});
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
