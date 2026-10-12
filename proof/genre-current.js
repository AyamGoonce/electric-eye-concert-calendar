(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b2379361c5afd3d7.js","sha256":"b2379361c5afd3d7c8d49e23c595411ea56e7c03f09f61bee51c25e151693c33","count":244});
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
