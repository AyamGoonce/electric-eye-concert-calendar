(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a4caa7971fe35af9.js","sha256":"a4caa7971fe35af96cd89c0770e9d6b19a68364d01bc4109ec2367e47d45b15c","count":179});
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
