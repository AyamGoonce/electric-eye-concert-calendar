(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3db31f6d6ca8a50a.js","sha256":"3db31f6d6ca8a50ac0522b0d6e98b833abd12a7012a8bff377e892c8a4a4c13f","count":244});
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
