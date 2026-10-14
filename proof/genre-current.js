(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.75e0d7c2b3a8ebef.js","sha256":"75e0d7c2b3a8ebefa45d32843eb94e812a4961bc423e64c8bf6749df59ed1761","count":244});
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
