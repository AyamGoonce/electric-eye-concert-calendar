(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a746cd70f182a4b9.js","sha256":"a746cd70f182a4b9cb7ae411467cabb55092f53ea64dddfce021f202622588b0","count":155});
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
