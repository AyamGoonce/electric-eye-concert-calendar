(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.831b20b22cd79ae4.js","sha256":"831b20b22cd79ae4d56c32cc66dadeb69942e1bbd2de4561ab2b0245822a65f6","count":109});
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
