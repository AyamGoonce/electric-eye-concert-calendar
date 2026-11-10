(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.291ec47e1bfa6d2d.js","sha256":"291ec47e1bfa6d2d9508738d3f9a717ac7306f0b617b2c025525d1626ea64ba5","count":244});
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
