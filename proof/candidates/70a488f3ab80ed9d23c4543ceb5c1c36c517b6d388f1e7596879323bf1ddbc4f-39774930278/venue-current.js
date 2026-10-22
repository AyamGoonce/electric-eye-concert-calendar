(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.9804f0e830c5785f.js","sha256":"9804f0e830c5785fa20ffb170b4803a062ddb1984169dfe187cd0d999fd821ed","count":156});
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
