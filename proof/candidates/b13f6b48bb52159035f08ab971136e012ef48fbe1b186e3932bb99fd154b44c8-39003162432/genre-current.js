(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.943d4680e2ee790e.js","sha256":"943d4680e2ee790e9c2f27a3b9e319609ab7bfbba028e474667b29d11b44c37f","count":244});
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
