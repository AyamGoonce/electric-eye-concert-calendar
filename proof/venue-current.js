(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.a5afcda806719380.js","sha256":"a5afcda806719380def5c180f3a9d1dd931a8432f7d1c6c7ebee7902f8947a19","count":149});
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
