(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c887e5ded225afa0.js","sha256":"c887e5ded225afa0277a8f5e051559d94d61c5cafd3d2a1422f167043109a9cf","count":208});
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
