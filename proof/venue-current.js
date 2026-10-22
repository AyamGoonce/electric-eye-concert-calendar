(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.8c8d843202bda786.js","sha256":"8c8d843202bda7862ff956204383817f392579827de14c14dd44e4847a4898a0","count":156});
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
