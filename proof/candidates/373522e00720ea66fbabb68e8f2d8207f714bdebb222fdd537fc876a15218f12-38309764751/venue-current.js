(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.98def9aa26568007.js","sha256":"98def9aa26568007508378f5e83edec06c7ab3ade8303fbabf6efdf89df8d231","count":165});
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
