(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.0ce97cbcb185636f.js","sha256":"0ce97cbcb185636fd230fc4267875a6598b403f4ac1b3467a88eea706caae07a","count":149});
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
