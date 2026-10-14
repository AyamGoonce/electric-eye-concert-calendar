(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0cda48c6da87fb5d.js","sha256":"0cda48c6da87fb5d8c835de998f9faf95a112cd0b286a6589c0c92accd49c712","count":164});
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
