(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.a741e6dc8f48d5f2.js","sha256":"a741e6dc8f48d5f208c1755e291bf98c1adcf55574b6e1b65d809b3d6f7be3ba","count":244});
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
