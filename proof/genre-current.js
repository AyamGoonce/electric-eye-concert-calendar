(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.0e266d656a3c5fc8.js","sha256":"0e266d656a3c5fc86087d9b844b0839e725239da808500cc2894a3ef325a5612","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
