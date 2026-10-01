(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.cc03c0de83a538b2.js","sha256":"cc03c0de83a538b292366d06677ed09822e3ff413f099b7a2b3912e4d767fc75","count":109});
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
