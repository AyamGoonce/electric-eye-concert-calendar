(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.8deb4fe2242f0472.js","sha256":"8deb4fe2242f0472b22dff17c0e40d3f8c42ec90a18309d495327a5f7f256ef5","count":244});
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
