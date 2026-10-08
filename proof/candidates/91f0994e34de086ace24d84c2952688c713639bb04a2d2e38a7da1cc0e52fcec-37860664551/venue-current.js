(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.64b436ea38be9177.js","sha256":"64b436ea38be9177e5d5dfd61a2d45947f9041ca545f814c0c89f439852f6e00","count":168});
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
