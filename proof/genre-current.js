(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7b33b6bb580b8977.js","sha256":"7b33b6bb580b89770e9eec10dcc15bf5bc51c3e028c154cc09e333fdf510ec15","count":244});
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
