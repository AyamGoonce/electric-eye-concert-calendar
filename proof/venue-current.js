(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5b775d135a52f70b.js","sha256":"5b775d135a52f70bcb0c39e16a067363c1d3feace5dc184c1fa2fb66c18403d5","count":154});
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
