(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.ca248bef60f7ae71.js","sha256":"ca248bef60f7ae710ac0914f187f8583269d88e8785232e900db824cb4bc8201","count":166});
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
