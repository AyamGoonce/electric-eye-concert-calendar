(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.3b404f33c038ece3.js","sha256":"3b404f33c038ece37bd02f0efde54dbd9f34f2566b1ca9c32a7496ac83e20715","count":181});
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
