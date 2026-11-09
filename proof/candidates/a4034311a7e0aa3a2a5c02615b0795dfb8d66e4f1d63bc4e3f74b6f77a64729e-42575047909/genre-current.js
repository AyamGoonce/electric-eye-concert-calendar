(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.5cebb8c84cc831f8.js","sha256":"5cebb8c84cc831f8eae99108c706a2ca4dedbbc50d8c35153c8d5c8e7a12654d","count":244});
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
