(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.53149fa03403cdc4.js","sha256":"53149fa03403cdc4f1e3c1a69776e8b4fe672a23978858640622b95647431655","count":176});
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
