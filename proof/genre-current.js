(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.46148a3b3796581a.js","sha256":"46148a3b3796581ac3f88dfd8bfbf5aee7e4f5522fbc58e9cafcdb51960aeaad","count":244});
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
