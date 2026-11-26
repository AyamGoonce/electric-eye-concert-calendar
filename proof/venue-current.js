(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.f5f7b908378637ce.js","sha256":"f5f7b908378637ce2bb6f58c37868357dd0feb810ef37f9356babab5b54144c9","count":181});
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
