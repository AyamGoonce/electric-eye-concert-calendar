(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.12b76fce2dc8c23a.js","sha256":"12b76fce2dc8c23aba83e6b408847899ee72027d57f779326e05aaa465104b83","count":180});
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
