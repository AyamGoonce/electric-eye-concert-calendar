(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.8a16dc48e017dde0.js","sha256":"8a16dc48e017dde01a4ca428a8d0aa8862ba1a82544eedb278f096332102cdbf","count":244});
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
