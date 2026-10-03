(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.2fccb8b5b9d4931b.js","sha256":"2fccb8b5b9d4931b1431aff1b5ecb99cda9b6c5ae8e566f0e7fdc83a991abd77","count":169});
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
