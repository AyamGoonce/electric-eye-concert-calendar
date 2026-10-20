(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.9f88b1d35a9a0763.js","sha256":"9f88b1d35a9a0763facc07d0024ffc0ddc8cd871f6af0fedf348670cd83b8367","count":244});
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
