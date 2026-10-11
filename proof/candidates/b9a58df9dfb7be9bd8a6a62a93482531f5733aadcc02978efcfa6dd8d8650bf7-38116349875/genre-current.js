(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c5fdf76a6677378d.js","sha256":"c5fdf76a6677378d2fd6f0a62508850621001c45a2b3a98b0e6b0c66fe835bbd","count":244});
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
