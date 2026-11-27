(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.45ec79ac0d488223.js","sha256":"45ec79ac0d48822342c9f45cfb325d95ed670ac9e13c8fc68d2dd351b00aec35","count":180});
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
