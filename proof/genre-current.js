(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ef474a75683d8a47.js","sha256":"ef474a75683d8a47c9a6bc96f4a0c0c9ff741a0b36033562b8ecbb04ccf60f82","count":244});
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
