(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.38123935ddde0ff7.js","sha256":"38123935ddde0ff76b2da97ceb6cef6037bbe4943b358e4f239554cd29bdb08c","count":244});
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
