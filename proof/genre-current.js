(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.11f461f9adaed63a.js","sha256":"11f461f9adaed63ac63fed609bdac430bf2bcda6e3d60aaa15500d3dfe4d0354","count":245});
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
