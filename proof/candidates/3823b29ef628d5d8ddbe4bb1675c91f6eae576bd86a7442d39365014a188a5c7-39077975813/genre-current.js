(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.964904bbf352aa92.js","sha256":"964904bbf352aa924ce21b084c9fa3ce8c6fda69dfa0c03f1eb8558b9f24e6c5","count":244});
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
