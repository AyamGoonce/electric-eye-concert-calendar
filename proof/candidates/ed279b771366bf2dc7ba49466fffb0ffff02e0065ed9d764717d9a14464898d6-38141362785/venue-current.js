(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0c616dbd8d7d245f.js","sha256":"0c616dbd8d7d245fdc44ee94a4e08d39b9e22bc22b70699255ca5056b68f2226","count":165});
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
