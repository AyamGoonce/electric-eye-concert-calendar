(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.df0f7ff3218d31d1.js","sha256":"df0f7ff3218d31d115a1f07fda7de8829f6958eec1bdb62c93b8ed914fa4b4b0","count":208});
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
