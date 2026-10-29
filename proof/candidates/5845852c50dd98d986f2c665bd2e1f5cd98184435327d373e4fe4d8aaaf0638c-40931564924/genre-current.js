(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c6d5b295d4b0d966.js","sha256":"c6d5b295d4b0d9662a0499dd7e2a3949e35f0fa8a94646c44f81cdaafedafeaf","count":244});
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
