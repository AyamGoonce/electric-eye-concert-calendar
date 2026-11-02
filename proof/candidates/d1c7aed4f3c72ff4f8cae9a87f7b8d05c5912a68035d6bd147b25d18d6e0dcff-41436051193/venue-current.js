(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0039b762a7f260de.js","sha256":"0039b762a7f260de2018d4d4cb3141bfd51ae09cf38de9a5858de083d93a321d","count":152});
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
