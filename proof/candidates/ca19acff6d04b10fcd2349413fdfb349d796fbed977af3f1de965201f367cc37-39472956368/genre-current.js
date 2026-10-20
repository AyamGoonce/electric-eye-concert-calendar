(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.4af98bbaceff77ed.js","sha256":"4af98bbaceff77ed24861b5c169cdf578126ea156d55df83f72b88dd6b30d67a","count":244});
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
